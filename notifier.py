# notifier.py
import json, socket, time
from pathlib import Path

def send_mqtt(cfg: dict, payload: dict):
    if not cfg.get("mqtt", {}).get("enabled", False):
        return
    try:
        import paho.mqtt.client as mqtt
        mcfg = cfg["mqtt"]
        cli = mqtt.Client()
        cli.connect(mcfg["broker"], int(mcfg.get("port",1883)), 60)
        cli.loop_start()
        cli.publish(mcfg["topic"], json.dumps(payload, ensure_ascii=False), qos=int(mcfg.get("qos",0)))
        time.sleep(0.2)
        cli.loop_stop(); cli.disconnect()
    except Exception as e:
        print("[MQTT] fail:", e)

def send_telegram(cfg: dict, text: str):
    if not cfg.get("telegram", {}).get("enabled", False):
        return
    try:
        import requests
        tcfg = cfg["telegram"]
        url = f"https://api.telegram.org/bot{tcfg['bot_token']}/sendMessage"
        data = {"chat_id": tcfg["chat_id"], "text": text}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("[TG] fail:", e)

def notify_all(cfg: dict, seat_id: str, reason: str, title: str, img_path: Path):
    host = socket.gethostname()
    payload = {
        "seat": seat_id,
        "host": host,
        "reason": reason,
        "title": title,
        "image": str(img_path),
        "ts": int(time.time())
    }
    send_mqtt(cfg, payload)
    msg = f"[경고] 좌석 {seat_id}: {reason} (제목: {title})"
    send_telegram(cfg, msg)
