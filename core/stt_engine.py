import sounddevice as sd
import vosk
import json
import queue
import os
from langdetect import detect


class SpeechToText:
    def __init__(self, config):
        self.language = config.get("language", "ru")

        # Модели для разных языков — ИМЕННО ТАК, КАК НАЗВАНЫ ПАПКИ У ТЕБЯ
        model_dir = {
            "ru": "vosk-model-ru-0.42",
            "uz": "vosk-model-small-uz-0.22",
            "en": "vosk-model-en-us-0.15",          # ← исправлено (без small)
            "ar": "vosk-model-ar-0.22-linto-1.1.0",
            "cn": "vosk-model-cn-0.22",
        }

        # Fallback по умолчанию — НОВАЯ русская модель
        default_model = "vosk-model-ru-0.42"

        model_name = model_dir.get(self.language, default_model)
        self.model_path = os.path.join("models", "stt", model_name)

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Модель не найдена: {self.model_path}")

        self.model = vosk.Model(self.model_path)
        self.q = queue.Queue()
        self.sample_rate = config.get("sample_rate", 16000)

    def _callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def listen_and_recognize(self):
        """
        Слушает микрофон, распознаёт речь.
        (Автоопределение языка можно доработать позже, сейчас главное — стабильная работа.)
        """
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback,
        ):
            rec = vosk.KaldiRecognizer(self.model, self.sample_rate)

            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()
                    if not text:
                        continue
                    return text
