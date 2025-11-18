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
