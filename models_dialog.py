"""
Диалог для управления моделями нейросетей
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialogButtonBox,
    QFormLayout, QLineEdit, QComboBox, QCheckBox, QLabel
)
from PyQt5.QtCore import Qt
import db


class ModelEditDialog(QDialog):
    """Диалог для добавления/редактирования модели"""
    def __init__(self, model_data=None, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.setWindowTitle("Редактировать модель" if model_data else "Добавить модель")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Например: GPT-4")
        layout.addRow("Название:", self.name_edit)
        
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("https://api.openai.com/v1/chat/completions")
        layout.addRow("API URL:", self.api_url_edit)
        
        self.api_id_edit = QLineEdit()
        self.api_id_edit.setPlaceholderText("gpt-4")
        layout.addRow("API ID модели:", self.api_id_edit)
        
        self.api_key_env_edit = QLineEdit()
        self.api_key_env_edit.setPlaceholderText("OPENAI_API_KEY")
        layout.addRow("Переменная API-ключа:", self.api_key_env_edit)
        
        self.model_type_combo = QComboBox()
        self.model_type_combo.addItems(["openai", "deepseek", "groq", "openrouter"])
        layout.addRow("Тип API:", self.model_type_combo)
        
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        layout.addRow("Активна:", self.is_active_checkbox)
        
        # Заполняем поля, если редактируем
        if model_data:
            self.name_edit.setText(model_data.get("name", ""))
            self.api_url_edit.setText(model_data.get("api_url", ""))
            self.api_id_edit.setText(model_data.get("api_id", ""))
            self.api_key_env_edit.setText(model_data.get("api_key_env", ""))
            index = self.model_type_combo.findText(model_data.get("model_type", "openai"))
            if index >= 0:
                self.model_type_combo.setCurrentIndex(index)
            self.is_active_checkbox.setChecked(model_data.get("is_active", 1) == 1)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Возвращает данные модели"""
        return {
            "name": self.name_edit.text().strip(),
            "api_url": self.api_url_edit.text().strip(),
            "api_id": self.api_id_edit.text().strip(),
            "api_key_env": self.api_key_env_edit.text().strip(),
            "model_type": self.model_type_combo.currentText(),
            "is_active": 1 if self.is_active_checkbox.isChecked() else 0
        }


class ModelsDialog(QDialog):
    """Диалог для управления моделями"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление моделями")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить модель")
        self.add_btn.clicked.connect(self.on_add_model)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.on_edit_model)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.on_delete_model)
        buttons_layout.addWidget(self.delete_btn)
        
        self.toggle_btn = QPushButton("Включить/Выключить")
        self.toggle_btn.clicked.connect(self.on_toggle_model)
        buttons_layout.addWidget(self.toggle_btn)
        
        buttons_layout.addStretch()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_models)
        buttons_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Таблица моделей
        self.models_table = QTableWidget()
        self.models_table.setColumnCount(6)
        self.models_table.setHorizontalHeaderLabels([
            "ID", "Название", "API URL", "API ID", "Тип", "Активна"
        ])
        self.models_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.models_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.models_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.models_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.models_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.models_table.setAlternatingRowColors(True)
        layout.addWidget(self.models_table)
        
        # Кнопки закрытия
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.accept)
        layout.addWidget(close_buttons)
        
        self.setLayout(layout)
        
        self.load_models()
    
    def load_models(self):
        """Загружает список моделей в таблицу"""
        models_list = db.get_models()
        self.models_table.setRowCount(len(models_list))
        
        for row, model in enumerate(models_list):
            self.models_table.setItem(row, 0, QTableWidgetItem(str(model["id"])))
            self.models_table.setItem(row, 1, QTableWidgetItem(model["name"]))
            self.models_table.setItem(row, 2, QTableWidgetItem(model["api_url"]))
            self.models_table.setItem(row, 3, QTableWidgetItem(model["api_id"]))
            self.models_table.setItem(row, 4, QTableWidgetItem(model["model_type"]))
            
            is_active = "Да" if model["is_active"] == 1 else "Нет"
            self.models_table.setItem(row, 5, QTableWidgetItem(is_active))
            
            # Делаем все ячейки нередактируемыми
            for col in range(6):
                item = self.models_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def get_selected_model_id(self):
        """Возвращает ID выбранной модели"""
        current_row = self.models_table.currentRow()
        if current_row >= 0:
            item = self.models_table.item(current_row, 0)
            if item:
                return int(item.text())
        return None
    
    def on_add_model(self):
        """Добавление новой модели"""
        dialog = ModelEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not all([data["name"], data["api_url"], data["api_id"], data["api_key_env"]]):
                QMessageBox.warning(self, "Предупреждение", "Заполните все поля")
                return
            
            try:
                db.add_model(
                    name=data["name"],
                    api_url=data["api_url"],
                    api_id=data["api_id"],
                    api_key_env=data["api_key_env"],
                    model_type=data["model_type"],
                    is_active=data["is_active"]
                )
                QMessageBox.information(self, "Успех", "Модель добавлена")
                self.load_models()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить модель: {e}")
    
    def on_edit_model(self):
        """Редактирование модели"""
        model_id = self.get_selected_model_id()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для редактирования")
            return
        
        model_data = db.get_model_by_id(model_id)
        if not model_data:
            QMessageBox.warning(self, "Предупреждение", "Модель не найдена")
            return
        
        dialog = ModelEditDialog(model_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not all([data["name"], data["api_url"], data["api_id"], data["api_key_env"]]):
                QMessageBox.warning(self, "Предупреждение", "Заполните все поля")
                return
            
            try:
                db.update_model(
                    model_id=model_id,
                    name=data["name"],
                    api_url=data["api_url"],
                    api_id=data["api_id"],
                    api_key_env=data["api_key_env"],
                    model_type=data["model_type"],
                    is_active=data["is_active"]
                )
                QMessageBox.information(self, "Успех", "Модель обновлена")
                self.load_models()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить модель: {e}")
    
    def on_delete_model(self):
        """Удаление модели"""
        model_id = self.get_selected_model_id()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить эту модель?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if db.delete_model(model_id):
                    QMessageBox.information(self, "Успех", "Модель удалена")
                    self.load_models()
                else:
                    QMessageBox.warning(self, "Предупреждение", "Не удалось удалить модель")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")
    
    def on_toggle_model(self):
        """Включение/выключение модели"""
        model_id = self.get_selected_model_id()
        if not model_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите модель")
            return
        
        model_data = db.get_model_by_id(model_id)
        if not model_data:
            return
        
        new_status = 0 if model_data["is_active"] == 1 else 1
        try:
            if db.update_model_status(model_id, new_status):
                status_text = "включена" if new_status == 1 else "выключена"
                QMessageBox.information(self, "Успех", f"Модель {status_text}")
                self.load_models()
            else:
                QMessageBox.warning(self, "Предупреждение", "Не удалось изменить статус")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")




