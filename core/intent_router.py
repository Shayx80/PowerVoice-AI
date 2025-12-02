class IntentRouter:
    """
    Простейший роутер намерений:
    - 'command' — если фраза похожа на команду
    - 'chat'    — обычный разговор
    """

    def detect_intent(self, text: str) -> str:
        if not text:
            return "chat"

        lowered = text.lower()

        command_keywords = [
            "открой",
            "запусти",
            "создай",
            "удали",
            "очисти",
            "покажи папку",
            "открой папку",
        ]

        if any(word in lowered for word in command_keywords):
            return "command"

        return "chat"
