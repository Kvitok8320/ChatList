"""
Диалог для управления промтами
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialogButtonBox,
    QFormLayout, QTextEdit, QLineEdit, QLabel
)
from PyQt5.QtCore import Qt
import db


class PromptEditDialog(QDialog):
    """Диалог для добавления/редактирования промта"""
    def __init__(self, prompt_data=None, parent=None):
        super().__init__(parent)
        self.prompt_data = prompt_data
        self.setWindowTitle("Редактировать промт" if prompt_data else "Добавить промт")
        self.setModal(True)
        self.setMinimumSize(500, 300)
        
        layout = QFormLayout()
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setMinimumHeight(150)
        layout.addRow("Промт:", self.prompt_edit)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("тег1, тег2, тег3")
        layout.addRow("Теги:", self.tags_edit)
        
        # Заполняем поля, если редактируем
        if prompt_data:
            self.prompt_edit.setPlainText(prompt_data.get("prompt", ""))
            self.tags_edit.setText(prompt_data.get("tags", "") or "")
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Возвращает данные промта"""
        return {
            "prompt": self.prompt_edit.toPlainText().strip(),
            "tags": self.tags_edit.text().strip() or None
        }


class PromptsDialog(QDialog):
    """Диалог для управления промтами"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление промтами")
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        
        # Поиск
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить промт")
        self.add_btn.clicked.connect(self.on_add_prompt)
        buttons_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.on_edit_prompt)
        buttons_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.on_delete_prompt)
        buttons_layout.addWidget(self.delete_btn)
        
        buttons_layout.addStretch()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_prompts)
        buttons_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Таблица промтов
        self.prompts_table = QTableWidget()
        self.prompts_table.setColumnCount(4)
        self.prompts_table.setHorizontalHeaderLabels(["ID", "Дата", "Промт", "Теги"])
        self.prompts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.prompts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.prompts_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.prompts_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.prompts_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.prompts_table.setAlternatingRowColors(True)
        layout.addWidget(self.prompts_table)
        
        # Кнопки закрытия
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.accept)
        layout.addWidget(close_buttons)
        
        self.setLayout(layout)
        
        self.load_prompts()
    
    def load_prompts(self, search_query=None):
        """Загружает список промтов в таблицу"""
        if search_query:
            prompts_list = db.search_prompts(search_query)
        else:
            prompts_list = db.get_prompts()
        
        self.prompts_table.setRowCount(len(prompts_list))
        
        for row, prompt in enumerate(prompts_list):
            self.prompts_table.setItem(row, 0, QTableWidgetItem(str(prompt["id"])))
            self.prompts_table.setItem(row, 1, QTableWidgetItem(prompt["date"][:19] if len(prompt["date"]) > 19 else prompt["date"]))
            
            prompt_text = prompt["prompt"][:100] + "..." if len(prompt["prompt"]) > 100 else prompt["prompt"]
            self.prompts_table.setItem(row, 2, QTableWidgetItem(prompt_text))
            
            tags = prompt.get("tags", "") or ""
            self.prompts_table.setItem(row, 3, QTableWidgetItem(tags))
            
            # Делаем все ячейки нередактируемыми
            for col in range(4):
                item = self.prompts_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    
    def on_search(self):
        """Обработчик поиска"""
        query = self.search_edit.text().strip()
        self.load_prompts(query if query else None)
    
    def get_selected_prompt_id(self):
        """Возвращает ID выбранного промта"""
        current_row = self.prompts_table.currentRow()
        if current_row >= 0:
            item = self.prompts_table.item(current_row, 0)
            if item:
                return int(item.text())
        return None
    
    def on_add_prompt(self):
        """Добавление нового промта"""
        dialog = PromptEditDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["prompt"]:
                QMessageBox.warning(self, "Предупреждение", "Введите текст промта")
                return
            
            try:
                db.add_prompt(data["prompt"], data["tags"])
                QMessageBox.information(self, "Успех", "Промт добавлен")
                self.load_prompts()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить промт: {e}")
    
    def on_edit_prompt(self):
        """Редактирование промта"""
        prompt_id = self.get_selected_prompt_id()
        if not prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите промт для редактирования")
            return
        
        prompt_data = db.get_prompt_by_id(prompt_id)
        if not prompt_data:
            QMessageBox.warning(self, "Предупреждение", "Промт не найден")
            return
        
        dialog = PromptEditDialog(prompt_data, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["prompt"]:
                QMessageBox.warning(self, "Предупреждение", "Введите текст промта")
                return
            
            # Обновление промта (нужно добавить функцию в db.py)
            try:
                # Пока просто удаляем и создаем заново
                db.delete_prompt(prompt_id)
                db.add_prompt(data["prompt"], data["tags"])
                QMessageBox.information(self, "Успех", "Промт обновлен")
                self.load_prompts()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить промт: {e}")
    
    def on_delete_prompt(self):
        """Удаление промта"""
        prompt_id = self.get_selected_prompt_id()
        if not prompt_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите промт для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить этот промт?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if db.delete_prompt(prompt_id):
                    QMessageBox.information(self, "Успех", "Промт удален")
                    self.load_prompts()
                else:
                    QMessageBox.warning(self, "Предупреждение", "Не удалось удалить промт")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")

