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
seat: A-01
host: student-PC
reason: template_match
title: ChatGPT 탐지됨
image: C:/ExamAgent/logs/20251119_093512.png
ts: 1763480932
---------------------------------------

=== 새 감지 이벤트 수신 ===
seat: A-01
host: student-PC
reason: template_match
title: ChatGPT 탐지됨
image: C:/ExamAgent/logs/20251119_093515.png
ts: 1763480935
---------------------------------------
