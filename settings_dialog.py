"""
Диалог настроек приложения
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import db


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.setMinimumSize(400, 250)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # Выбор темы
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Темная", "dark")
        form_layout.addRow("Тема:", self.theme_combo)
        
        # Выбор размера шрифта
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" pt")
        form_layout.addRow("Размер шрифта:", self.font_size_spin)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Загружаем текущие настройки
        self.load_settings()
    
    def load_settings(self):
        """Загружает текущие настройки из БД"""
        theme = db.get_setting("theme", "light")
        font_size = db.get_setting("font_size", "10")
        
        # Устанавливаем тему
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Устанавливаем размер шрифта
        try:
            self.font_size_spin.setValue(int(font_size))
        except ValueError:
            self.font_size_spin.setValue(10)
    
    def on_save(self):
        """Сохранение настроек"""
        theme = self.theme_combo.currentData()
        font_size = str(self.font_size_spin.value())
        
        try:
            db.save_setting("theme", theme)
            db.save_setting("font_size", font_size)
            QMessageBox.information(self, "Успех", "Настройки сохранены и применены.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def get_theme(self) -> str:
        """Возвращает выбранную тему"""
        return self.theme_combo.currentData()
    
    def get_font_size(self) -> int:
        """Возвращает выбранный размер шрифта"""
        return self.font_size_spin.value()

