@echo off
REM Content OS always-on launcher (target of the Startup-folder entry). Self-locating:
REM cd to the project root wherever it is started from.
cd /d "%~dp0.."
if not exist data\logs mkdir data\logs
:loop
echo [%date% %time%] starting Content OS >> data\logs\server.log
node server\index.ts >> data\logs\server.log 2>&1
REM index.ts exits 0 at once when another instance already owns the port: stop then.
if %errorlevel%==0 goto :eof
echo [%date% %time%] Content OS exited with %errorlevel%, restarting in 15s >> data\logs\server.log
timeout /t 15 /nobreak >nul
goto loop
