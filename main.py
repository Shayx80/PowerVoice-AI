from core.autostart_manager import (
    load_config,
    ensure_autostart,
    log_startup,
    show_notification,
)
from gui.main_window import start_gui


if __name__ == "__main__":
    # Загружаем настройки
    config = load_config()

    # Обеспечиваем автозапуск, если включен в настройках
    if config.get("autostart", True):
        ensure_autostart()

    # Лог + уведомление
    log_startup("✅ Power Voice запущен успешно.")
    show_notification("Power Voice", "✅ Ассистент запущен и готов к работе!")

    # Запускаем GUI
    start_gui()
