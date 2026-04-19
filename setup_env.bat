@echo off
cd /d %~dp0

echo ================================
echo  BOT .ENV YARATISH
 echo ================================
set /p BOT_TOKEN=BotFather tokenni kiriting: 
set /p ADMIN_IDS=Admin ID larni kiriting (vergul bilan): 
(
  echo BOT_TOKEN=%BOT_TOKEN%
  echo ADMIN_IDS=%ADMIN_IDS%
) > .env

echo.
echo .env tayyor bo'ldi.
echo Endi start_bot.bat ni ishga tushiring.
pause
