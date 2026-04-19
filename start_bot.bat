@echo off
cd /d %~dp0
if not exist .env (
  echo .env topilmadi. Avval setup_env.bat ni ishga tushiring.
  pause
  exit /b 1
)
python -m app.bot
pause
