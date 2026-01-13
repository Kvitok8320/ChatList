"""
Тестовая программа для просмотра и редактирования SQLite баз данных
"""
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
    QFileDialog, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QTextEdit, QSpinBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import List, Dict, Optional


class EditRecordDialog(QDialog):
    """Диалог для редактирования записи"""
    def __init__(self, table_name: str, columns: List[str], record_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.record_data = record_data
        self.is_new = record_data is None
        
        self.setWindowTitle(f"{'Добавить' if self.is_new else 'Редактировать'} запись в {table_name}")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        self.fields = {}
        form_layout = QFormLayout()
        
        for col in columns:
            if self.is_new or col not in record_data:
                value = ""
            else:
                value = str(record_data.get(col, ""))
            
            if len(value) > 100 or "\n" in value:
                # Для длинных текстов используем QTextEdit
                field = QTextEdit()
                field.setPlainText(value)
                field.setMaximumHeight(100)
            else:
                # Для коротких значений используем QLineEdit
                field = QLineEdit()
                field.setText(value)
            
            self.fields[col] = field
            form_layout.addRow(f"{col}:", field)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_data(self) -> Dict[str, str]:
        """Возвращает данные из формы"""
        data = {}
        for col, field in self.fields.items():
            if isinstance(field, QTextEdit):
                data[col] = field.toPlainText()
            else:
                data[col] = field.text()
        return data


class TableViewDialog(QDialog):
    """Диалог для просмотра и редактирования таблицы с пагинацией"""
    def __init__(self, db_path: str, table_name: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.table_name = table_name
        self.current_page = 1
        self.page_size = 50
        self.total_records = 0
        
        self.setWindowTitle(f"Таблица: {table_name}")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout()
        
        # Информация о таблице
        info_label = QLabel(f"Таблица: {table_name} | Всего записей: {self.total_records}")
        info_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(info_label)
        
        # Пагинация
        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(QLabel("Страница:"))
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(1)
        self.page_spin.valueChanged.connect(self.on_page_changed)
        pagination_layout.addWidget(self.page_spin)
        
        pagination_layout.addWidget(QLabel(f"из"))
        self.total_pages_label = QLabel("1")
        pagination_layout.addWidget(self.total_pages_label)
        
        pagination_layout.addWidget(QLabel("Записей на странице:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setMinimum(10)
        self.page_size_spin.setMaximum(500)
        self.page_size_spin.setValue(self.page_size)
        self.page_size_spin.valueChanged.connect(self.on_page_size_changed)
        pagination_layout.addWidget(self.page_size_spin)
        
        pagination_layout.addStretch()
        
        self.refresh_btn = QPushButton("Обновить")
        self.refresh_btn.clicked.connect(self.load_table)
        pagination_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(pagination_layout)
        
        # Кнопки CRUD
        crud_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.on_add_record)
        crud_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Редактировать")
        self.edit_btn.clicked.connect(self.on_edit_record)
        crud_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Удалить")
        self.delete_btn.clicked.connect(self.on_delete_record)
        crud_layout.addWidget(self.delete_btn)
        
        crud_layout.addStretch()
        
        layout.addLayout(crud_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Запрещаем прямое редактирование
        layout.addWidget(self.table)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Загружаем таблицу
        self.load_table()
    
    def get_connection(self):
        """Создает соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_table_info(self):
        """Получает информацию о таблице"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем количество записей
        cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
        self.total_records = cursor.fetchone()[0]
        
        # Получаем названия колонок
        cursor.execute(f"PRAGMA table_info({self.table_name})")
        columns_info = cursor.fetchall()
        columns = [col[1] for col in columns_info]  # col[1] - это имя колонки
        
        conn.close()
        return columns
    
    def load_table(self):
        """Загружает данные таблицы с пагинацией"""
        try:
            columns = self.get_table_info()
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            
            # Вычисляем пагинацию
            total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
            self.page_spin.setMaximum(total_pages)
            self.total_pages_label.setText(str(total_pages))
            
            offset = (self.current_page - 1) * self.page_size
            
            # Загружаем данные
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} LIMIT ? OFFSET ?", (self.page_size, offset))
            rows = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(rows))
            
            for row_idx, row in enumerate(rows):
                for col_idx, col_name in enumerate(columns):
                    value = row[col_name] if col_name in row.keys() else ""
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row_idx, col_idx, item)
            
            # Настраиваем ширину колонок
            self.table.resizeColumnsToContents()
            
            # Обновляем информацию
            info_label = self.findChild(QLabel)
            if info_label:
                info_label.setText(f"Таблица: {self.table_name} | Всего записей: {self.total_records} | Страница {self.current_page} из {total_pages}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить таблицу: {e}")
    
    def on_page_changed(self, page: int):
        """Обработчик изменения страницы"""
        self.current_page = page
        self.load_table()
    
    def on_page_size_changed(self, size: int):
        """Обработчик изменения размера страницы"""
        self.page_size = size
        self.current_page = 1
        self.page_spin.setValue(1)
        self.load_table()
    
    def get_selected_row_data(self) -> Optional[Dict]:
        """Получает данные выбранной строки"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return None
        
        columns = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        data = {}
        for col_idx, col_name in enumerate(columns):
            item = self.table.item(current_row, col_idx)
            data[col_name] = item.text() if item else ""
        
        return data
    
    def on_add_record(self):
        """Добавление новой записи"""
        try:
            columns = self.get_table_info()
            dialog = EditRecordDialog(self.table_name, columns, None, self)
            
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                
                # Формируем SQL запрос
                columns_str = ", ".join(data.keys())
                placeholders = ", ".join(["?" for _ in data])
                values = list(data.values())
                
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(f"INSERT INTO {self.table_name} ({columns_str}) VALUES ({placeholders})", values)
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Успех", "Запись добавлена")
                self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись: {e}")
    
    def on_edit_record(self):
        """Редактирование записи"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для редактирования")
            return
        
        try:
            columns = self.get_table_info()
            data = self.get_selected_row_data()
            
            if not data:
                QMessageBox.warning(self, "Предупреждение", "Не удалось получить данные записи")
                return
            
            dialog = EditRecordDialog(self.table_name, columns, data, self)
            
            if dialog.exec_() == QDialog.Accepted:
                new_data = dialog.get_data()
                
                # Получаем первичный ключ (предполагаем, что первая колонка - это ID)
                primary_key_col = columns[0]
                primary_key_value = data[primary_key_col]
                
                # Формируем SQL запрос для обновления
                set_clause = ", ".join([f"{col} = ?" for col in new_data.keys()])
                values = list(new_data.values()) + [primary_key_value]
                
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(f"UPDATE {self.table_name} SET {set_clause} WHERE {primary_key_col} = ?", values)
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Успех", "Запись обновлена")
                self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись: {e}")
    
    def on_delete_record(self):
        """Удаление записи"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись для удаления")
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить эту запись?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            columns = self.get_table_info()
            data = self.get_selected_row_data()
            
            if not data:
                QMessageBox.warning(self, "Предупреждение", "Не удалось получить данные записи")
                return
            
            # Получаем первичный ключ
            primary_key_col = columns[0]
            primary_key_value = data[primary_key_col]
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE {primary_key_col} = ?", (primary_key_value,))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Успех", "Запись удалена")
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {e}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Просмотр SQLite базы данных")
        self.setGeometry(100, 100, 600, 500)
        self.db_path = None
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Кнопка выбора файла
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        file_layout.addWidget(self.file_label)
        
        self.select_file_btn = QPushButton("Выбрать файл SQLite")
        self.select_file_btn.clicked.connect(self.on_select_file)
        file_layout.addWidget(self.select_file_btn)
        
        layout.addLayout(file_layout)
        
        # Список таблиц
        tables_label = QLabel("Таблицы в базе данных:")
        tables_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(tables_label)
        
        self.tables_list = QTableWidget()
        self.tables_list.setColumnCount(2)
        self.tables_list.setHorizontalHeaderLabels(["Таблица", "Действие"])
        self.tables_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tables_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tables_list.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.tables_list)
        
        # Кнопка обновления
        refresh_btn = QPushButton("Обновить список таблиц")
        refresh_btn.clicked.connect(self.load_tables)
        layout.addWidget(refresh_btn)
    
    def on_select_file(self):
        """Выбор файла SQLite"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл SQLite",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if filename:
            self.db_path = filename
            self.file_label.setText(f"Файл: {filename}")
            self.load_tables()
    
    def get_tables(self) -> List[str]:
        """Получает список таблиц из базы данных"""
        if not self.db_path:
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к базе данных: {e}")
            return []
    
    def load_tables(self):
        """Загружает список таблиц"""
        if not self.db_path:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите файл базы данных")
            return
        
        tables = self.get_tables()
        self.tables_list.setRowCount(len(tables))
        
        for row, table_name in enumerate(tables):
            # Название таблицы
            name_item = QTableWidgetItem(table_name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.tables_list.setItem(row, 0, name_item)
            
            # Кнопка "Открыть"
            open_btn = QPushButton("Открыть")
            open_btn.clicked.connect(lambda checked, t=table_name: self.on_open_table(t))
            self.tables_list.setCellWidget(row, 1, open_btn)
    
    def on_open_table(self, table_name: str):
        """Открывает диалог просмотра таблицы"""
        if not self.db_path:
            return
        
        dialog = TableViewDialog(self.db_path, table_name, self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

