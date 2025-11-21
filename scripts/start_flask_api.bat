@echo off
REM 启动Flask API服务 (Windows)

cd /d "%~dp0\.."
python poc\hr\apis\flask_server.py

