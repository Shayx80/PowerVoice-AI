import os
import json
import winreg
from datetime import datetime

# Базовый конфиг по умолчанию (совпадает с settings.json)
DEFAULT_CONFIG = {
    "language": "ru",
    "voice": "female",
    "mode": "offline",
    "sample_rate": 16000,
    "device": "cpu",
    "trial_days": 14,
    "license_key": "",
    "owner_id": "MASTER",
    "vip_users": [],
    "hotkey": "Ctrl+Shift+Space",
    "llm_primary": "mistral-7b-instruct-v0.3.Q4_K_M.gguf",
    "llm_secondary": "meta-llama-3-8b-instruct.Q4_K_M.gguf",
    "languages_supported": {
        "ru": "vosk-model-ru-0.42",
        "uz": "vosk-model-small-uz-0.22",
        "en": "vosk-model-en-us-0.15",
        "ar": "vosk-model-ar-0.22-linto-1.1.0",
        "cn": "vosk-model-cn-0.22"
    },
    "auto_language_detect": True,
    "auto_repair_config": True,
    "auto_start_listening": True,
    "internet_access_button": True,
    "autostart": True
}


def show_notification(title: str, message: str):
    """Сейчас просто выводит сообщение в консоль (без win11toast)."""
    print(f"[NOTIFY] {title}: {message}")


def add_autostart() -> bool:
    """Добавляет Power Voice в автозагрузку через реестр."""
    app_name = "Power Voice"
    pythonw = os.path.join("C:\\", "ai_voice_assistant", "venv", "Scripts", "pythonw.exe")
    script_path = os.path.join("C:\\", "ai_voice_assistant", "main.py")
    command = f'"{pythonw}" "{script_path}"'

    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print("✅ Power Voice добавлен в автозагрузку.")
        return True
    except Exception as e:
        print(f"⚠️ Не удалось добавить в автозагрузку: {e}")
        return False


def remove_autostart() -> bool:
    """Удаляет Power Voice из автозагрузки."""
    app_name = "Power Voice"
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, app_name)
        winreg.CloseKey(key)
        print("🧹 Power Voice удалён из автозагрузки.")
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"⚠️ Ошибка при удалении из автозагрузки: {e}")
        return False


def is_autostart_enabled() -> bool:
    """Проверяет, есть ли запись автозапуска в реестре."""
    app_name = "Power Voice"
    reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
        current_value, _ = winreg.QueryValueEx(key, app_name)
        winreg.CloseKey(key)
        return bool(current_value)
    except FileNotFoundError:
        return False


def ensure_autostart():
    """Включает автозапуск, если его ещё нет."""
    if not is_autostart_enabled():
        added = add_autostart()
        if added:
            print("🟡 Автозапуск активирован впервые.")


def load_config() -> dict:
    """Загружает settings.json, при повреждении — восстанавливает по DEFAULT_CONFIG."""
    cfg_path = os.path.join("config", "settings.json")

    if not os.path.exists(cfg_path):
        os.makedirs("config", exist_ok=True)
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        print("🛠 Создан новый settings.json.")
        return DEFAULT_CONFIG.copy()

    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("settings.json повреждён (не dict).")

        changed = False
        for k, v in DEFAULT_CONFIG.items():
            if k not in data:
                data[k] = v
                changed = True

        if changed:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("🔧 settings.json автоматически поправлен.")

        return data

    except Exception as e:
        print(f"⚠️ Ошибка чтения settings.json ({e}). Восстанавливаю по умолчанию.")
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONFIG.copy()


def log_startup(message: str):
    """Пишет лог запуска в C:\\ai_voice_assistant\\logs\\startup_log.txt."""
    log_dir = os.path.join("C:\\", "ai_voice_assistant", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "startup_log.txt")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
