import os
import json
import datetime


class LicenseManager:
    """
    Менеджер лицензии.
    Поддерживает:
    - Локальную проверку
    - Пробный период
    - VIP и владельца
    """

    def __init__(self, config=None):
        self.config = config or {}
        self.license_file = os.path.join("config", "license.json")
        self.trial_days = self.config.get("trial_days", 14)
        self.owner_id = self.config.get("owner_id", "MASTER")
        self.vip_users = set(self.config.get("vip_users", []))
        self.license_key = self.config.get("license_key", "")

        # Автоинициализация
        self._ensure_license_file()

    def _ensure_license_file(self):
        if not os.path.exists(self.license_file):
            data = {
                "created": datetime.date.today().isoformat(),
                "license_key": self.license_key,
                "owner": self.owner_id,
                "active": True
            }
            os.makedirs("config", exist_ok=True)
            with open(self.license_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def get_status(self):
        try:
            with open(self.license_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return "⚠️ Ошибка чтения лицензии"

        if data.get("owner") == self.owner_id:
            return "✅ Владелец (без ограничений)"

        if data.get("license_key"):
            return "✅ Активирована лицензия"

        # Проверка пробного периода
        try:
            start = datetime.date.fromisoformat(data.get("created"))
            days = (datetime.date.today() - start).days
        except Exception:
            return "⚠️ Ошибка даты лицензии"

        if days <= self.trial_days:
            left = self.trial_days - days
            return f"🕓 Пробный период: {left} дней осталось"
        else:
            return "❌ Срок пробного периода истёк"

    def is_active(self):
        status = self.get_status()
        return any(keyword in status for keyword in ["✅", "🕓"])
