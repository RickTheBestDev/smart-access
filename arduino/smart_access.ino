#include <Servo.h>

const int TRIG_PIN = 9;
const int ECHO_PIN = 10;
const int SERVO_PIN = 6;
const int LED_GREEN = 2;
const int LED_YELLOW = 3;
const int LED_RED = 4;
const int BUZZER_PIN = 5;

const float DETECTION_DISTANCE_CM = 25.0;
const unsigned long SENSOR_INTERVAL_MS = 300;
const unsigned long AUTO_OPEN_MS = 3000;

Servo barrierServo;
bool autoMode = false;       // Inicia em manual por segurança.
bool barrierOpen = false;    // Estado lógico comandado.
bool presenceDetected = false;
float distanceCm = -1;
unsigned long lastSensorRead = 0;
unsigned long openedAt = 0;
unsigned long lastTelemetry = 0;

void setBarrier(bool openBarrier) {
  barrierOpen = openBarrier;
  barrierServo.write(openBarrier ? 90 : 0);
  updateLeds();
}

void updateLeds() {
  digitalWrite(LED_GREEN, barrierOpen ? HIGH : LOW);
  digitalWrite(LED_RED, barrierOpen ? LOW : HIGH);
  digitalWrite(LED_YELLOW, presenceDetected ? HIGH : LOW);
}

float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  unsigned long duration = pulseIn(ECHO_PIN, HIGH, 30000UL);
  if (duration == 0) return -1;
  return duration * 0.0343 / 2.0;
}

void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  if (command == "OPEN") {
    setBarrier(true);
    openedAt = millis();
    Serial.println("{\"event\":\"OPEN_COMMAND\"}");
  } else if (command == "CLOSE") {
    setBarrier(false);
    Serial.println("{\"event\":\"CLOSE_COMMAND\"}");
  } else if (command == "MODE_AUTO") {
    autoMode = true;
    Serial.println("{\"event\":\"MODE_AUTO\"}");
  } else if (command == "MODE_MANUAL") {
    autoMode = false;
    Serial.println("{\"event\":\"MODE_MANUAL\"}");
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  barrierServo.attach(SERVO_PIN);
  setBarrier(false);
  Serial.println("{\"event\":\"BOOT\",\"barrier_state\":\"CLOSED\",\"mode\":\"MANUAL\"}");
}

void loop() {
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }

  unsigned long now = millis();
  if (now - lastSensorRead >= SENSOR_INTERVAL_MS) {
    lastSensorRead = now;
    distanceCm = readDistanceCm();
    presenceDetected = (distanceCm >= 0 && distanceCm <= DETECTION_DISTANCE_CM);
    updateLeds();

    if (autoMode && presenceDetected && !barrierOpen) {
      setBarrier(true);
      openedAt = now;
      tone(BUZZER_PIN, 1500, 150);
    }
    if (autoMode && barrierOpen && !presenceDetected &&
        now - openedAt >= AUTO_OPEN_MS) {
      setBarrier(false);
    }
    if (presenceDetected) tone(BUZZER_PIN, 1000, 60);
  }

  if (now - lastTelemetry >= 1000) {
    lastTelemetry = now;
    Serial.print("{\"distance_cm\":");
    if (distanceCm < 0) Serial.print("null"); else Serial.print(distanceCm, 1);
    Serial.print(",\"presence_detected\":");
    Serial.print(presenceDetected ? "true" : "false");
    Serial.print(",\"barrier_state\":\"");
    Serial.print(barrierOpen ? "OPEN" : "CLOSED");
    Serial.print("\",\"mode\":\"");
    Serial.print(autoMode ? "AUTO" : "MANUAL");
    Serial.print("\",\"timestamp_ms\":");
    Serial.print(millis());
    Serial.println("}");
  }
}
