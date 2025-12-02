import os
import datetime


class SkillManager:
    """
    Примитивные локальные команды:
    - сказать время
    - очистить временные файлы
    - открыть текущую папку
    """

    def execute(self, command: str, is_online: bool = False) -> str:
        cmd = command.lower()

        if "время" in cmd:
            return f"Сейчас {datetime.datetime.now().strftime('%H:%M')}"

        if "очисти временные" in cmd or "очисти временные файлы" in cmd:
            os.system('del /q data\\tmp\\*')
            return "Временные файлы очищены."

        if "папку" in cmd or "открой папку" in cmd:
            os.system("start explorer .")
            return "Открываю текущую папку."

        return "Команда не распознана."
