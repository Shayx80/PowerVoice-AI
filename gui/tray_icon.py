import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer


class TrayManager:
    """
    Менеджер иконки Power Voice в системном трее.
    Поддерживает:
    - мигающую подсветку при активном прослушивании
    - переключение режима онлайн/оффлайн
    - управление главным окном и выходом
    """

    def __init__(self, app, main_window=None, icon_path="assets/icons/pv_icon.ico"):
        self.app = app
        self.main_window = main_window
        self.icon_path = icon_path if os.path.exists(icon_path) else None

        if not self.icon_path:
            QMessageBox.warning(None, "Ошибка", "Иконка PV не найдена!")
            return

        # создаём трей и меню
        self.tray = QSystemTrayIcon(QIcon(self.icon_path), self.app)
        self.menu = QMenu()

        # состояния
        self.active = True
        self.internet_enabled = True
        self.blink_state = True

        # действия меню
        self.toggle_action = QAction("⏸ Приостановить", self.app)
        self.toggle_action.triggered.connect(self.toggle_assistant)

        self.internet_action = QAction("🌐 Интернет: ВКЛ", self.app)
        self.internet_action.triggered.connect(self.toggle_internet)

        self.open_panel_action = QAction("⚙ Панель управления", self.app)
        self.open_panel_action.triggered.connect(self.open_panel)

        self.exit_action = QAction("❌ Выход", self.app)
        self.exit_action.triggered.connect(self.exit_app)

        # добавляем в меню
        self.menu.addAction(self.toggle_action)
        self.menu.addAction(self.internet_action)
        self.menu.addSeparator()
        self.menu.addAction(self.open_panel_action)
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)

        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip("Power Voice — ИИ-Голосовой Ассистент")
        self.tray.show()

        # Мягкое мигание иконки (не скрывает полностью)
        self.timer = QTimer()
        self.timer.timeout.connect(self._blink_icon)
        self.timer.start(2000)

        # Левая кнопка мыши — показать окно
        self.tray.activated.connect(self._on_click)

    # -----------------------------
    # Методы управления
    # -----------------------------
    def toggle_assistant(self):
        """Приостановить или возобновить голосового ассистента"""
        if not self.main_window:
            return

        if self.active:
            self.main_window._stop_listening()
            self.toggle_action.setText("▶ Возобновить")
            self.tray.showMessage("PV", "Ассистент приостановлен ⏸", QSystemTrayIcon.MessageIcon.Information)
        else:
            self.main_window._start_listening()
            self.toggle_action.setText("⏸ Приостановить")
            self.tray.showMessage("PV", "Ассистент снова слушает 🎙", QSystemTrayIcon.MessageIcon.Information)

        self.active = not self.active

    def toggle_internet(self):
        """Переключить режим онлайн/оффлайн"""
        self.internet_enabled = not self.internet_enabled
        if self.internet_enabled:
            self.internet_action.setText("🌐 Интернет: ВКЛ")
            self.tray.showMessage("Power Voice", "Интернет доступен ✅", QSystemTrayIcon.MessageIcon.Information)
            if hasattr(self.main_window, "network"):
                self.main_window._on_network_status_changed(True)
        else:
            self.internet_action.setText("🌐 Интернет: ВЫКЛ")
            self.tray.showMessage("Power Voice", "Режим офлайн активирован 📴", QSystemTrayIcon.MessageIcon.Warning)
            if hasattr(self.main_window, "network"):
                self.main_window._on_network_status_changed(False)

    def open_panel(self):
        """Показать основное окно"""
        if self.main_window:
            self.main_window.showNormal()
            self.main_window.activateWindow()
        else:
            self.tray.showMessage("Power Voice", "Панель управления не найдена!")

    def exit_app(self):
        """Корректно выйти"""
        self.tray.showMessage("Power Voice", "Ассистент завершает работу ❌")
        if self.main_window:
            try:
                self.main_window.voice_listener.stop()
            except Exception:
                pass
            try:
                self.main_window.network.stop()
            except Exception:
                pass
        QTimer.singleShot(800, self.app.quit)

    def _blink_icon(self):
        """Мягкое мигание, если ассистент слушает"""
        if not self.active:
            return
        opacity = 1.0 if self.blink_state else 0.6
        self.tray.setIcon(QIcon(self.icon_path))
        self.tray.setToolTip(f"Power Voice — слушаю... 🎧" if self.blink_state else "Power Voice — в ожидании...")
        self.blink_state = not self.blink_state

    def _on_click(self, reason):
        """ЛКМ по иконке — открыть окно"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.open_panel()
