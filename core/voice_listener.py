import threading
from typing import Callable


class VoiceListener:
    """
    Фоновый голосовой слушатель:
    - постоянно вызывает stt.listen_and_recognize()
    - при получении текста вызывает callback(text)
    """

    def __init__(self, stt_engine, on_text: Callable[[str], None]):
        self.stt_engine = stt_engine
        self.on_text = on_text
        self._stop_event = threading.Event()
        self._thread = None

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                text = self.stt_engine.listen_and_recognize()
            except Exception as e:
                # при желании можно логировать в файл
                continue

            if not text:
                continue

            if self.on_text:
                try:
                    self.on_text(text)
                except Exception:
                    # не даём потоку упасть
                    continue

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
