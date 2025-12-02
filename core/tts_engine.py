import pyttsx3
from langdetect import detect

class TextToSpeech:
    """
    Локальный синтез речи с автоопределением языка.
    Работает полностью офлайн.
    """

    def __init__(self, config):
        self.config = config
        self.engine = pyttsx3.init()
        self.voice_gender = config.get("voice", "female")
        self._setup_default_voice()

    def _setup_default_voice(self):
        """Выбираем подходящий голос по умолчанию"""
        voices = self.engine.getProperty("voices")
        for v in voices:
            if "female" in self.voice_gender and "female" in v.name.lower():
                self.engine.setProperty("voice", v.id)
                return
        self.engine.setProperty("voice", voices[0].id)

    def _set_voice_by_language(self, lang_code: str):
        """Подбирает голос по языку (ru, en, ar, uz)"""
        voices = self.engine.getProperty("voices")

        # соответствие языков
        lang_map = {
            "ru": ["ru", "russian"],
            "en": ["en", "english"],
            "uz": ["uz", "uzbek"],
            "ar": ["ar", "arabic"]
        }

        for v in voices:
            name = v.name.lower()
            for key, tags in lang_map.items():
                if lang_code.startswith(key) or any(t in name for t in tags):
                    self.engine.setProperty("voice", v.id)
                    return True
        return False

    def speak(self, text: str):
        """Озвучивает текст на нужном языке"""
        try:
            lang = detect(text)
            self._set_voice_by_language(lang)
        except Exception:
            pass  # fallback на стандартный голос

        self.engine.say(text)
        self.engine.runAndWait()
