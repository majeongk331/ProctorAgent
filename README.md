# ProctorAgent

cmd
taskkill /IM ProctorAgent.exe /F
cd %USERPROFILE%\Desktop\ProctorAgent
pyinstaller --onefile --noconsole --name ProctorAgent agent.py ^
  --add-data "config.yaml;." ^
  --add-data "templates;templates" 
