import json
import os
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
    QMessageBox,
)

from core.stt_engine import SpeechToText
from core.tts_engine import TextToSpeech
from core.nlp_engine import NlpProcessor
from core.intent_router import IntentRouter
from core.skill_manager import SkillManager
from core.license_manager import LicenseManager
from core.network_manager import NetworkManager
from core.voice_listener import VoiceListener
from core.autostart_manager import add_autostart, remove_autostart, is_autostart_enabled


class GuiSignals(QObject):
    append_log = pyqtSignal(str)
    update_net_status = pyqtSignal(bool)


class VoiceAssistantGUI(QMainWindow):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Power Voice — Мультиязычный ИИ Голосовой Ассистент")
        self.resize(900, 600)

        self.config = config
        self.is_listening = False
        self.is_online = False

        self.signals = GuiSignals()
        self.signals.append_log.connect(self._append_log)
        self.signals.update_net_status.connect(self._update_network_label)

        self._init_ui()
        self._init_ai()

    # -----------------------------
    # UI
    # -----------------------------
    def _init_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Строка состояния
        status_layout = QHBoxLayout()
        self.net_label = QLabel("⚙️ Режим: офлайн")
        self.net_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.license_label = QLabel("Лицензия: проверка...")
        self.license_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        status_layout.addWidget(self.net_label)
        status_layout.addWidget(self.license_label)

        # Лог
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        # Кнопки
        buttons_layout = QHBoxLayout()

        self.btn_listen = QPushButton("🎙 Запустить прослушивание")
        self.btn_listen.clicked.connect(self._toggle_listening)

        self.btn_check_net = QPushButton("🌐 Проверить интернет")
        self.btn_check_net.clicked.connect(self._manual_check_network)

        self.btn_autostart = QPushButton()
        self.btn_autostart.clicked.connect(self._toggle_autostart)
        self._update_autostart_button()

        buttons_layout.addWidget(self.btn_listen)
        buttons_layout.addWidget(self.btn_check_net)
        buttons_layout.addWidget(self.btn_autostart)

        layout.addLayout(status_layout)
        layout.addWidget(self.log)
        layout.addLayout(buttons_layout)

    # -----------------------------
    # AI инициализация
    # -----------------------------
    def _init_ai(self):
        try:
            self.stt = SpeechToText(self.config)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка STT", f"Не удалось загрузить модель речи:\n{e}")
            self.stt = None

        self.tts = TextToSpeech(self.config)
        self.nlp = NlpProcessor(self.config)
        self.router = IntentRouter()
        self.skills = SkillManager()
        self.license = LicenseManager(self.config)

        self.license_label.setText(f"Лицензия: {self.license.get_status()}")

        # Сеть
        self.network = NetworkManager(check_interval=600)
        self.network.start(callback=self._on_network_status_changed)

        # Слушатель
        if self.stt:
            self.voice_listener = VoiceListener(self.stt, self._on_voice_text)
        else:
            self.voice_listener = None

        self._append_log("🤖 Ассистент готов к работе.")

    # -----------------------------
    # Автозапуск
    # -----------------------------
    def _update_autostart_button(self):
        if is_autostart_enabled():
            self.btn_autostart.setText("🚫 Отключить автозапуск")
            self.btn_autostart.setStyleSheet("background-color: #f5d442; color: black; font-weight: bold;")
        else:
            self.btn_autostart.setText("⚡ Включить автозапуск")
            self.btn_autostart.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

    def _toggle_autostart(self):
        cfg_path = os.path.join("config", "settings.json")
        enabled = is_autostart_enabled()

        if enabled:
            remove_autostart()
            self.config["autostart"] = False
            QMessageBox.information(self, "Power Voice", "🧹 Автозапуск отключён.")
        else:
            add_autostart()
            self.config["autostart"] = True
            QMessageBox.information(self, "Power Voice", "⚡ Автозапуск включён.")

        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        self._update_autostart_button()

    # -----------------------------
    # Сеть
    # -----------------------------
    def _on_network_status_changed(self, is_online: bool):
        self.signals.update_net_status.emit(is_online)

    def _update_network_label(self, is_online: bool):
        self.is_online = is_online
        if is_online:
            self.net_label.setText("🌐 Режим: онлайн (интернет доступен)")
        else:
            self.net_label.setText("⚙️ Режим: офлайн (работа локально)")

    def _manual_check_network(self):
        from core.network_manager import NetworkManager as NM
        nm = NM()
        status = nm._check_once()
        self._on_network_status_changed(status)
        msg = "Интернет доступен ✅" if status else "Интернет недоступен ❌"
        QMessageBox.information(self, "Проверка сети", msg)

    # -----------------------------
    # Прослушивание
    # -----------------------------
    def _start_listening(self):
        if self.is_listening or not self.voice_listener:
            return
        self.is_listening = True
        self.btn_listen.setText("⏸ Остановить прослушивание")
        self.voice_listener.start()
        self._append_log("🎙 Прослушивание запущено.")

    def _stop_listening(self):
        if not self.is_listening or not self.voice_listener:
            return
        self.is_listening = False
        self.btn_listen.setText("🎙 Запустить прослушивание")
        self.voice_listener.stop()
        self._append_log("⏸ Прослушивание остановлено.")

    def _toggle_listening(self):
        if self.is_listening:
            self._stop_listening()
        else:
            self._start_listening()

    # -----------------------------
    # Обработка речи
    # -----------------------------
    def _on_voice_text(self, text: str):
        if not text.strip():
            return
        self.signals.append_log.emit(f"👤 Вы: {text}")

        try:
            intent = self.router.detect_intent(text)
        except Exception:
            intent = "chat"

        try:
            if intent == "command":
                response = self.skills.execute(text, is_online=self.is_online)
                if not response:
                    response = "Команда выполнена."
            else:
                response = self.nlp.generate_response(text)
        except Exception as e:
            response = f"Ошибка при обработке: {e}"

        self.signals.append_log.emit(f"🤖 Ассистент: {response}")

        try:
            self.tts.speak(response)
        except Exception:
            pass

    # -----------------------------
    # Лог
    # -----------------------------
    def _append_log(self, text: str):
        self.log.append(text)

    # -----------------------------
    # Закрытие окна
    # -----------------------------
    def closeEvent(self, event):
        try:
            if self.voice_listener:
                self.voice_listener.stop()
        except Exception:
            pass
        try:
            self.network.stop()
        except Exception:
            pass
        event.accept()


def start_gui():
    import sys
    try:
        from gui.tray_icon import TrayManager
    except Exception:
        TrayManager = None

    config_path = os.path.join("config", "settings.json")
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        config = {
            "language": "ru",
            "voice": "female",
            "mode": "offline",
            "sample_rate": 16000,
            "device": "cpu",
            "trial_days": 14,
            "license_key": "",
            "autostart": True,
            "llm_primary": "mistral-7b-instruct-v0.3.Q4_K_M.gguf",
            "llm_secondary": "meta-llama-3-8b-instruct.Q4_K_M.gguf",
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    else:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            config = {}

    app = QApplication(sys.argv)
    window = VoiceAssistantGUI(config)
    if TrayManager:
        tray = TrayManager(app, window)
    window.show()
    sys.exit(app.exec())
