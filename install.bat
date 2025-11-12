@echo off
setlocal

set APPDIR=%USERPROFILE%\Desktop\ProctorAgent
set LOGDIR=%USERPROFILE%\Desktop\ProctorAgent\logs

echo [*] Installing ProctorAgent ...

if not exist "%APPDIR%" mkdir "%APPDIR%"
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

xcopy "%~dp0..\*" "%APPDIR%\" /E /I /Y >nul

schtasks /Create /TN "ProctorAgent" /SC ONSTART /RL HIGHEST /RU SYSTEM /TR "\"%APPDIR%\ProctorAgent.exe\"" /F

echo [*] ProctorAgent installed and scheduled to run at startup.
echo [*] Logs: %LOGDIR%
pause