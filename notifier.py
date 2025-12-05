# notifier.py — ProctorAgent에서 MQTT로 알림 보내기
import json
import time
import socket
import paho.mqtt.client as mqtt

def notify_all(cfg: dict, seat_id: str, reason: str, title: str, img_path):
    mqtt_cfg = cfg.get("mqtt", {})
    if not mqtt_cfg.get("enabled", False):
        return

    broker = mqtt_cfg.get("broker", "192.168.137.154")
    port   = int(mqtt_cfg.get("port", 1883))
    topic  = mqtt_cfg.get("topic", "exam/agent/events")
    host   = socket.gethostname()

    payload = {
        "seat": seat_id,
        "host": host,
        "reason": reason,
        "title": title,
        "image": str(img_path),
        "ts": int(time.time())
    }

    try:
        cli = mqtt.Client()
        cli.connect(broker, port, 60)
        cli.publish(topic, json.dumps(payload, ensure_ascii=False), qos=1)
        cli.disconnect()
        print("MQTT notify sent:", payload)
    except Exception as e:
        print("MQTT notify error:", e)
