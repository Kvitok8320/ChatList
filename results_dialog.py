"""
Диалог для просмотра сохраненных результатов
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDialogButtonBox,
    QLineEdit, QLabel
)
from PyQt5.QtCore import Qt
import db
from markdown_viewer import MarkdownViewerDialog


class ResultsDialog(QDialog):
    """Диалог для просмотра сохраненных результатов"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сохраненные результаты")
        self.setMinimumSize(1000, 600)
        
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
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.on_delete_result)
        buttons_layout.addWidget(self.delete_btn)
        
        buttons_layout.addStretch()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_results)
        buttons_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(buttons_layout)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Модель", "Промт", "Ответ", "Действия"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        # Включаем перенос текста
        self.results_table.setWordWrap(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)
        
        # Кнопки закрытия
        close_buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_buttons.rejected.connect(self.accept)
        layout.addWidget(close_buttons)
        
        self.setLayout(layout)
        
        self.load_results()
    
    def load_results(self, search_query=None):
        """Загружает список результатов в таблицу"""
        if search_query:
            results_list = db.search_results(search_query)
        else:
            results_list = db.get_results()
        
        self.results_table.setRowCount(len(results_list))
        
        for row, result in enumerate(results_list):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(result["id"])))
            
            date = result["date"][:19] if len(result["date"]) > 19 else result["date"]
            self.results_table.setItem(row, 1, QTableWidgetItem(date))
            
            model_name = result.get("model_name", "Неизвестно") or "Неизвестно"
            self.results_table.setItem(row, 2, QTableWidgetItem(model_name))
            
            prompt_text = result.get("prompt_text", "")[:80] + "..." if len(result.get("prompt_text", "")) > 80 else result.get("prompt_text", "")
            self.results_table.setItem(row, 3, QTableWidgetItem(prompt_text))
            
            response = result.get("response", "")[:200] + "..." if len(result.get("response", "")) > 200 else result.get("response", "")
            response_item = QTableWidgetItem(response)
            response_item.setToolTip(result.get("response", ""))  # Полный текст в подсказке
            self.results_table.setItem(row, 4, response_item)
            
            # Кнопка "Открыть" для просмотра полного ответа в markdown
            open_btn = QPushButton("Открыть")
            open_btn.clicked.connect(lambda checked, r=row: self.on_open_response(r))
            self.results_table.setCellWidget(row, 5, open_btn)
            
            # Делаем все ячейки нередактируемыми
            for col in range(5):
                item = self.results_table.item(row, col)
                if item:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        
        # Автоматически подстраиваем высоту строк
        self.results_table.resizeRowsToContents()
        # Устанавливаем минимальную высоту строк
        for row in range(self.results_table.rowCount()):
            self.results_table.setRowHeight(row, max(80, self.results_table.rowHeight(row)))
    
    def on_search(self):
        """Обработчик поиска"""
        query = self.search_edit.text().strip()
        self.load_results(query if query else None)
    
    def get_selected_result_id(self):
        """Возвращает ID выбранного результата"""
        current_row = self.results_table.currentRow()
        if current_row >= 0:
            item = self.results_table.item(current_row, 0)
            if item:
                return int(item.text())
        return None
    
    def on_delete_result(self):
        """Удаление результата"""
        result_id = self.get_selected_result_id()
        if not result_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите результат для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить этот результат?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if db.delete_result(result_id):
                    QMessageBox.information(self, "Успех", "Результат удален")
                    self.load_results()
                else:
                    QMessageBox.warning(self, "Предупреждение", "Не удалось удалить результат")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {e}")
    
    def on_open_response(self, row: int):
        """Открывает полный ответ в диалоге с форматированным markdown"""
        if row < 0 or row >= self.results_table.rowCount():
            return
        
        # Получаем ID результата из первой колонки
        id_item = self.results_table.item(row, 0)
        model_item = self.results_table.item(row, 2)
        
        if not id_item or not model_item:
            return
        
        result_id = int(id_item.text())
        model_name = model_item.text()
        
        # Получаем полный ответ из базы данных
        try:
            result_data = db.get_result_by_id(result_id)
            if not result_data:
                QMessageBox.warning(self, "Предупреждение", "Результат не найден в базе данных")
                return
            
            full_response = result_data.get("response", "")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке ответа: {e}")
            return
        
        if not full_response:
            QMessageBox.information(self, "Информация", "Ответ пуст")
            return
        
        # Открываем диалог с форматированным markdown
        dialog = MarkdownViewerDialog(model_name, full_response, self)
        dialog.exec_()




