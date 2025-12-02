@echo off
chcp 65001 >nul
echo === Добавление Power Voice в автозапуск через Планировщик ===

set "TASKNAME=PowerVoice_Autostart"
set "PYTHONW=C:\ai_voice_assistant\venv\Scripts\pythonw.exe"
set "SCRIPT=C:\ai_voice_assistant\main.py"

:: Удаляем старое задание (если было)
schtasks /delete /f /tn "%TASKNAME%" >nul 2>&1

:: Создаём новое
schtasks /create /tn "%TASKNAME%" /tr "\"%PYTHONW%\" \"%SCRIPT%\"" /sc onlogon /rl highest /delay 0000:10 /f

if %errorlevel%==0 (
    echo ✅ Задание успешно создано.
    echo ⚡ Power Voice будет запускаться при входе в систему.
) else (
    echo ❌ Ошибка при создании задания.
)
timeout /t 3 >nul
exit /b
