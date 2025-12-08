# ProctorAgent

cmd
taskkill /IM ProctorAgent.exe /F

cd %USERPROFILE%\Desktop\ProctorAgent
pyinstaller --onefile --noconsole --name ProctorAgent agent.py ^
  --add-data "config.yaml;." ^
  --add-data "templates;templates" 

pyinstaller --onefile --noconsole --name ProctorUI ProctorUI.py


#관리자 권한
cd "C\Program Files\mosquitto"
mosquitto -v -c mosquitto.conf # -> 통신 준비

python mqtt_logger.py


MQTT client started
on_connect rc = 0
Subscribed to exam/agent/events

=== 새 감지 이벤트 수신 ===
Topic : exam/agent/events
Seat  : A-01
Host  : 마정북
Reason: template_match
Title : "특허 출원 절차 안내 - Chrome"
Image : C:\Users\highq\Desktop\ProctorAgent\logs\images\susp_20251202_164800.png
TS    : 1764661687
