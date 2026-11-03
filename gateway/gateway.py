
import json
import re
import threading
import time
from datetime import UTC, datetime

import paho.mqtt.client as mqtt
import serial

# CONFIGURAÇÕES MQTT
MQTT_HOST = "192.168.137.1"
MQTT_PORT = 1883

TOPIC_COMMAND = "smartaccess/command"
TOPIC_TELEMETRY = "smartaccess/telemetry"


# CONFIGURAÇÕES SERIAL
SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 9600

# Intervalo mínimo entre publicações de distância
INTERVALO_TELEMETRIA = 3.0


# ESTADO DO SISTEMA
arduino: serial.Serial | None = None
serial_lock = threading.Lock()

modo = "AUTO"
estado_cancela = "CLOSED"
ultima_distancia = None
ultima_publicacao_distancia = 0.0


def publicar_telemetria(client):
    dados = {
        "distance_cm": ultima_distancia,
        "presence_detected": (
            ultima_distancia is not None
            and ultima_distancia < 25
        ),
        "barrier_state": estado_cancela,
        "mode": modo,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    resultado = client.publish(
        TOPIC_TELEMETRY,
        json.dumps(dados),
        qos=1
    )

    if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Telemetria publicada:", dados)
    else:
        print("Erro ao publicar telemetria:", resultado.rc)


def conectar_arduino():
    global arduino

    while arduino is None:
        try:
            arduino = serial.Serial(
                SERIAL_PORT,
                SERIAL_BAUD,
                timeout=1
            )

            time.sleep(2)
            print("Arduino conectado em", SERIAL_PORT)

        except serial.SerialException as erro:
            print("Aguardando Arduino:", erro)
            time.sleep(3)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("MQTT conectado: Success")
        client.subscribe(TOPIC_COMMAND)
        print("Inscrito em", TOPIC_COMMAND)
    else:
        print("Falha na conexão MQTT:", reason_code)


def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))

        if isinstance(payload, dict):
            comando = str(
                payload.get("command", payload.get("action", ""))
            ).upper()
        else:
            comando = str(payload).upper()

        comandos = {
            "OPEN": "O",
            "CLOSE": "C",
            "AUTO": "A",
            "AUTOMATIC": "A",
            "MANUAL": "M",
            "MODE_AUTO": "A",
            "MODE_MANUAL": "M",
            "O": "O",
            "C": "C",
            "A": "A",
            "M": "M",
        }

        if comando not in comandos:
            print("Comando desconhecido:", payload)
            return

        with serial_lock:
            conexao = arduino

            if conexao is None or not conexao.is_open:
                print("Arduino não está conectado.")
                return

            conexao.write(comandos[comando].encode("utf-8"))

        print("Comando:", comando, "-> Arduino:", comandos[comando])

    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as erro:
        print("Mensagem inválida:", erro)

    except serial.SerialException as erro:
        print("Erro na comunicação serial:", erro)


def processar_mensagem(client, mensagem):
    global modo, estado_cancela
    global ultima_distancia, ultima_publicacao_distancia

    texto = mensagem.strip()

    if not texto:
        return

    resultado = re.search(
        r"Distancia filtrada:\s*([\d.]+)\s*cm",
        texto
    )

    if resultado:
        ultima_distancia = float(resultado.group(1))
        agora = time.monotonic()

        if agora - ultima_publicacao_distancia >= INTERVALO_TELEMETRIA:
            ultima_publicacao_distancia = agora
            publicar_telemetria(client)

        return

    print("Arduino:", texto)

    if "Modo AUTOMATICO ativado" in texto:
        modo = "AUTO"
        publicar_telemetria(client)

    elif "Modo MANUAL ativado" in texto:
        modo = "MANUAL"
        publicar_telemetria(client)

    elif texto == "Modo AUTOMATICO":
        modo = "AUTO"
        publicar_telemetria(client)

    elif "Cancela aberta" in texto:
        estado_cancela = "OPEN"
        publicar_telemetria(client)

    elif "Cancela fechada" in texto:
        estado_cancela = "CLOSED"
        publicar_telemetria(client)


def main():
    conectar_arduino()

    client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,  # type: ignore[attr-defined]
    client_id="smartaccess-gateway"
)
    

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    print("Gateway Smart Access iniciado")

    try:
        while True:
            try:
                with serial_lock:
                    conexao = arduino

                    if conexao is None or not conexao.is_open:
                        print("Arduino não está conectado.")
                        time.sleep(1)
                        continue

                    linha = conexao.readline()

                if linha:
                    texto = linha.decode(
                        "utf-8",
                        errors="replace"
                    )

                    processar_mensagem(client, texto)

            except serial.SerialException as erro:
                print("Erro ao ler Arduino:", erro)
                time.sleep(1)

    except KeyboardInterrupt:
        print("\nEncerrando gateway...")

    finally:
        client.loop_stop()
        client.disconnect()

        if arduino is not None and arduino.is_open:
            arduino.close()


if __name__ == "__main__":
    main()
