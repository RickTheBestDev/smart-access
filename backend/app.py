
import json
import os
import sqlite3
from datetime import UTC, datetime

import paho.mqtt.client as mqtt
from flask import Flask, jsonify, request
from flask_cors import CORS
from paho.mqtt.enums import CallbackAPIVersion

import database

app = Flask(__name__)
CORS(app)

database.init_db()

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_ENABLED = os.getenv("MQTT_ENABLED", "0") == "1"

mqtt_client = None
mqtt_connected = False


def on_connect(client, userdata, flags, reason_code, properties=None):
    global mqtt_connected

    mqtt_connected = reason_code == 0

    if mqtt_connected:
        client.subscribe("smartaccess/telemetry")
        print("Conectado ao MQTT; inscrito em smartaccess/telemetry")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        database.save_telemetry(data)

    except (json.JSONDecodeError, UnicodeDecodeError, TypeError, ValueError, sqlite3.Error) as exc:
        database.record_event(
            "ERROR",
            f"Mensagem MQTT inválida: {exc}",
            source="backend"
        )
        print("Erro ao processar mensagem MQTT:", exc)


def start_mqtt():
    global mqtt_client

    if not MQTT_ENABLED:
        print("MQTT desativado. Defina MQTT_ENABLED=1 quando o broker estiver disponível.")
        return

    mqtt_client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id="smartaccess-api"
    )

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
    mqtt_client.loop_start()


@app.get("/api/health")
def health():
    return jsonify({
        "api": "ok",
        "mqtt_enabled": MQTT_ENABLED,
        "mqtt_connected": mqtt_connected
    })


@app.get("/api/status")
def status():
    return jsonify(database.get_latest())


@app.get("/api/events")
def events():
    try:
        limit = max(1, min(int(request.args.get("limit", 50)), 200))
    except ValueError:
        limit = 50

    return jsonify(database.get_events(limit))


@app.post("/api/telemetry")
def telemetry():
    """Endpoint de teste local para simular dados."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or "distance_cm" not in data:
        return jsonify({
            "error": "Envie um JSON com distance_cm."
        }), 400

    try:
        data["distance_cm"] = float(data["distance_cm"])

        if not 0 <= data["distance_cm"] <= 450:
            return jsonify({
                "error": "distance_cm deve estar entre 0 e 450."
            }), 400

    except (TypeError, ValueError):
        return jsonify({
            "error": "distance_cm deve ser numérico."
        }), 400

    data.setdefault("presence_detected", data["distance_cm"] < 25)
    data.setdefault("barrier_state", "CLOSED")
    data.setdefault("mode", "MANUAL")
    data.setdefault("timestamp", datetime.now(UTC).isoformat())

    database.save_telemetry(data)

    return jsonify({
        "ok": True,
        "saved": data
    }), 201


@app.post("/api/commands")
def commands():
    data = request.get_json(silent=True) or {}
    action = str(data.get("action", "")).upper()

    allowed = {"OPEN", "CLOSE", "MODE_AUTO", "MODE_MANUAL"}

    if action not in allowed:
        return jsonify({
            "error": f"Comando inválido. Use um de: {', '.join(sorted(allowed))}."
        }), 400

    if mqtt_client is None or not mqtt_connected:
        database.record_event(
            "COMMAND_REJECTED",
            f"Comando {action} não enviado: MQTT indisponível",
            source="api"
        )

        return jsonify({
            "error": "MQTT indisponível. O comando não foi enviado ao hardware.",
            "action": action
        }), 503

    payload = json.dumps({
        "action": action,
        "source": "web",
        "timestamp": datetime.now(UTC).isoformat()
    })

    info = mqtt_client.publish(
        "smartaccess/command",
        payload,
        qos=1
    )

    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        return jsonify({
            "error": "Falha ao publicar comando MQTT."
        }), 502

    database.record_event(
        "COMMAND_SENT",
        f"Comando enviado: {action}",
        source="web"
    )

    return jsonify({
        "ok": True,
        "action": action,
        "message": "Comando publicado; aguarde telemetria para confirmar o estado lógico."
    }), 202


if __name__ == "__main__":
    start_mqtt()
    app.run(host="127.0.0.1", port=5000, debug=False)
