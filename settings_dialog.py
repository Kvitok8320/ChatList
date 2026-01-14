"""
Диалог настроек приложения
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QFormLayout, QDialogButtonBox, QMessageBox,
    QLineEdit, QTabWidget, QWidget, QTextEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import db
import os
from app_paths import get_app_data_dir
from dotenv import load_dotenv, set_key


class SettingsDialog(QDialog):
    """Диалог настроек приложения"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        
        # Вкладка "Внешний вид"
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout()
        appearance_form = QFormLayout()
        
        # Выбор темы
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Светлая", "light")
        self.theme_combo.addItem("Темная", "dark")
        appearance_form.addRow("Тема:", self.theme_combo)
        
        # Выбор размера шрифта
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" pt")
        appearance_form.addRow("Размер шрифта:", self.font_size_spin)
        
        appearance_layout.addLayout(appearance_form)
        appearance_layout.addStretch()
        appearance_tab.setLayout(appearance_layout)
        
        # Вкладка "API ключи"
        api_keys_tab = QWidget()
        api_keys_layout = QVBoxLayout()
        api_keys_form = QFormLayout()
        
        # Информационное сообщение
        info_label = QLabel(
            "Введите ваши API ключи. Ключи сохраняются локально в вашей папке данных.\n"
            "Каждый пользователь должен использовать свои собственные ключи."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; padding: 10px;")
        api_keys_layout.addWidget(info_label)
        
        # Поля для API ключей
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        self.openai_key_edit.setPlaceholderText("sk-...")
        api_keys_form.addRow("OpenAI API Key:", self.openai_key_edit)
        
        self.deepseek_key_edit = QLineEdit()
        self.deepseek_key_edit.setEchoMode(QLineEdit.Password)
        self.deepseek_key_edit.setPlaceholderText("sk-...")
        api_keys_form.addRow("DeepSeek API Key:", self.deepseek_key_edit)
        
        self.groq_key_edit = QLineEdit()
        self.groq_key_edit.setEchoMode(QLineEdit.Password)
        self.groq_key_edit.setPlaceholderText("gsk_...")
        api_keys_form.addRow("Groq API Key:", self.groq_key_edit)
        
        self.openrouter_key_edit = QLineEdit()
        self.openrouter_key_edit.setEchoMode(QLineEdit.Password)
        self.openrouter_key_edit.setPlaceholderText("sk-or-v1-...")
        api_keys_form.addRow("OpenRouter API Key:", self.openrouter_key_edit)
        
        api_keys_layout.addLayout(api_keys_form)
        api_keys_layout.addStretch()
        api_keys_tab.setLayout(api_keys_layout)
        
        # Добавляем вкладки
        self.tabs.addTab(appearance_tab, "Внешний вид")
        self.tabs.addTab(api_keys_tab, "API ключи")
        
        layout.addWidget(self.tabs)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Загружаем текущие настройки
        self.load_settings()
    
    def load_settings(self):
        """Загружает текущие настройки из БД и .env файла"""
        # Загружаем настройки внешнего вида
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
        
        # Загружаем API ключи из .env файла
        # Ищем .env в пользовательской папке данных
        env_path = os.path.join(get_app_data_dir(), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        # Загружаем ключи из переменных окружения (если они уже установлены)
        import os as os_module
        openai_key = os_module.getenv("OPENAI_API_KEY", "")
        deepseek_key = os_module.getenv("DEEPSEEK_API_KEY", "")
        groq_key = os_module.getenv("GROQ_API_KEY", "")
        openrouter_key = os_module.getenv("OPENROUTER_API_KEY", "")
        
        # Показываем только последние 4 символа для безопасности
        if openai_key:
            self.openai_key_edit.setText(openai_key)
        if deepseek_key:
            self.deepseek_key_edit.setText(deepseek_key)
        if groq_key:
            self.groq_key_edit.setText(groq_key)
        if openrouter_key:
            self.openrouter_key_edit.setText(openrouter_key)
    
    def save_api_keys(self):
        """Сохраняет API ключи в .env файл в пользовательской папке"""
        env_path = os.path.join(get_app_data_dir(), '.env')
        
        # Создаем или обновляем .env файл
        keys_to_save = {
            "OPENAI_API_KEY": self.openai_key_edit.text().strip(),
            "DEEPSEEK_API_KEY": self.deepseek_key_edit.text().strip(),
            "GROQ_API_KEY": self.groq_key_edit.text().strip(),
            "OPENROUTER_API_KEY": self.openrouter_key_edit.text().strip()
        }
        
        # Читаем существующий .env файл, если он есть
        existing_keys = {}
        if os.path.exists(env_path):
            load_dotenv(env_path)
            import os as os_module
            for key in keys_to_save.keys():
                value = os_module.getenv(key, "")
                if value:
                    existing_keys[key] = value
        
        # Обновляем только непустые ключи
        updated = False
        for key, value in keys_to_save.items():
            if value:  # Сохраняем только если ключ не пустой
                if existing_keys.get(key) != value:
                    set_key(env_path, key, value)
                    updated = True
            elif key in existing_keys:
                # Если ключ пустой, но был установлен ранее, не удаляем его
                pass
        
        # Перезагружаем переменные окружения
        if updated:
            load_dotenv(env_path, override=True)
            return True
        return False
    
    def on_save(self):
        """Сохранение настроек"""
        try:
            # Сохраняем настройки внешнего вида
            theme = self.theme_combo.currentData()
            font_size = str(self.font_size_spin.value())
            
            db.save_setting("theme", theme)
            db.save_setting("font_size", font_size)
            
            # Сохраняем API ключи
            api_keys_saved = self.save_api_keys()
            
            message = "Настройки сохранены и применены."
            if api_keys_saved:
                # Перезагружаем переменные окружения в модуле network
                try:
                    import network
                    network.reload_env()
                    message += "\n\nAPI ключи сохранены и применены. Можно сразу использовать модели."
                except Exception as e:
                    message += f"\n\nAPI ключи сохранены, но требуется перезапуск приложения для применения."
            
            QMessageBox.information(self, "Успех", message)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def get_theme(self) -> str:
        """Возвращает выбранную тему"""
        return self.theme_combo.currentData()
    
    def get_font_size(self) -> int:
        """Возвращает выбранный размер шрифта"""
        return self.font_size_spin.value()

