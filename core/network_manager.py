import threading
import time
import requests


class NetworkManager:
    """
    Менеджер сети:
    - проверяет, есть ли интернет
    - периодически обновляет статус
    - даёт флаг is_online для остальных модулей
    """

    def __init__(self, check_interval: int = 600):
        self.check_interval = check_interval  # секунды (по умолчанию 10 минут)
        self.is_online = False
        self._stop_event = threading.Event()
        self._thread = None

    def _check_once(self) -> bool:
        try:
            # можно заменить на любой стабильный сайт
            requests.get("https://www.google.com", timeout=3)
            return True
        except Exception:
            return False

    def start(self, callback=None):
        """
        Запуск фоновой проверки сети.
        callback(is_online: bool) будет вызываться при изменении состояния.
        """
        self.is_online = self._check_once()
        if callback:
            try:
                callback(self.is_online)
            except Exception:
                pass

        def _loop():
            while not self._stop_event.is_set():
                status = self._check_once()
                if status != self.is_online:
                    self.is_online = status
                    if callback:
                        try:
                            callback(self.is_online)
                        except Exception:
                            pass
                time.sleep(self.check_interval)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
