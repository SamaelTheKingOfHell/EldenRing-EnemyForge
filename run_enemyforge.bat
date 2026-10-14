@echo off
cd /d "%~dp0"
python run_enemyforge.py %*
if %ERRORLEVEL% neq 0 pause
