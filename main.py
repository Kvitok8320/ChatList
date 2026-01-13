"""
Главный модуль приложения ChatList
Графический интерфейс для сравнения ответов нейросетей
"""
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QComboBox,
    QLabel, QCheckBox, QMessageBox, QHeaderView, QLineEdit, QDialog,
    QDialogButtonBox, QFormLayout, QMenuBar, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from typing import List, Dict, Optional
import db
import models
import export
from models_dialog import ModelsDialog
from prompts_dialog import PromptsDialog
from results_dialog import ResultsDialog
from markdown_viewer import MarkdownViewerDialog


class WorkerThread(QThread):
    """Поток для выполнения запросов к API в фоновом режиме"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt
    
    def run(self):
        """Выполняет запросы к моделям"""
        try:
            results = models.send_prompt_to_models(self.prompt)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class SavePromptDialog(QDialog):
    """Диалог для сохранения промта"""
    def __init__(self, prompt_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сохранить промт")
        self.setModal(True)
        
        layout = QFormLayout()
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(prompt_text)
        self.prompt_edit.setMaximumHeight(100)
        layout.addRow("Промт:", self.prompt_edit)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("тег1, тег2, тег3")
        layout.addRow("Теги:", self.tags_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def get_prompt(self) -> str:
        return self.prompt_edit.toPlainText()
    
    def get_tags(self) -> str:
        return self.tags_edit.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatList - Сравнение ответов нейросетей")
        self.setGeometry(100, 100, 1200, 800)
        
        # Инициализация базы данных
        db.init_db()
        
        # Временная таблица результатов в памяти
        self.temp_results: List[Dict] = []
        
        # Поток для выполнения запросов
        self.worker_thread: Optional[WorkerThread] = None
        
        self.init_ui()
        self.load_prompts()
        self.create_menu()
    
    def create_menu(self):
        """Создает меню приложения"""
        menubar = self.menuBar()
        
        # Меню "Управление"
        manage_menu = menubar.addMenu("Управление")
        
        models_action = manage_menu.addAction("Модели...")
        models_action.triggered.connect(self.on_manage_models)
        
        prompts_action = manage_menu.addAction("Промты...")
        prompts_action.triggered.connect(self.on_manage_prompts)
        
        results_action = manage_menu.addAction("Результаты...")
        results_action.triggered.connect(self.on_view_results)
        
        # Меню "Экспорт"
        export_menu = menubar.addMenu("Экспорт")
        
        export_md_action = export_menu.addAction("Экспорт в Markdown...")
        export_md_action.triggered.connect(lambda: self.on_export("markdown"))
        
        export_json_action = export_menu.addAction("Экспорт в JSON...")
        export_json_action.triggered.connect(lambda: self.on_export("json"))
        
        export_txt_action = export_menu.addAction("Экспорт в TXT...")
        export_txt_action.triggered.connect(lambda: self.on_export("text"))
    
    def init_ui(self):
        """Инициализация интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # === Область работы с промтами ===
        prompt_group = QWidget()
        prompt_layout = QVBoxLayout()
        prompt_group.setLayout(prompt_layout)
        
        # Заголовок
        prompt_label = QLabel("Промт:")
        prompt_label.setFont(QFont("Arial", 10, QFont.Bold))
        prompt_layout.addWidget(prompt_label)
        
        # Горизонтальный layout для выбора промта и кнопок
        prompt_controls = QHBoxLayout()
        
        # Выпадающий список сохраненных промтов
        self.prompt_combo = QComboBox()
        self.prompt_combo.setEditable(False)
        self.prompt_combo.currentIndexChanged.connect(self.on_prompt_selected)
        self.prompt_combo.setMinimumWidth(300)
        prompt_controls.addWidget(QLabel("Выбрать промт:"))
        prompt_controls.addWidget(self.prompt_combo)
        
        # Кнопка "Выбрать промт"
        self.select_prompt_btn = QPushButton("Выбрать")
        self.select_prompt_btn.clicked.connect(self.on_select_prompt)
        prompt_controls.addWidget(self.select_prompt_btn)
        
        prompt_controls.addStretch()
        
        # Кнопка "Сохранить промт"
        self.save_prompt_btn = QPushButton("Сохранить промт")
        self.save_prompt_btn.clicked.connect(self.on_save_prompt)
        prompt_controls.addWidget(self.save_prompt_btn)
        
        prompt_layout.addLayout(prompt_controls)
        
        # Область ввода промта
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Введите ваш промт здесь или выберите из сохраненных...")
        self.prompt_edit.setMinimumHeight(100)
        prompt_layout.addWidget(self.prompt_edit)
        
        # Кнопка "Отправить запрос"
        self.send_btn = QPushButton("Отправить запрос")
        self.send_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.send_btn.clicked.connect(self.on_send_request)
        self.send_btn.setMinimumHeight(40)
        prompt_layout.addWidget(self.send_btn)
        
        main_layout.addWidget(prompt_group)
        
        # === Область результатов ===
        results_group = QWidget()
        results_layout = QVBoxLayout()
        results_group.setLayout(results_layout)
        
        # Заголовок
        results_label = QLabel("Результаты:")
        results_label.setFont(QFont("Arial", 10, QFont.Bold))
        results_layout.addWidget(results_label)
        
        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Выбрать", "Модель", "Ответ", "Действия"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        # Включаем перенос текста для многострочного отображения ответов
        self.results_table.setWordWrap(True)
        # Устанавливаем минимальную высоту строк для лучшей читаемости
        self.results_table.verticalHeader().setDefaultSectionSize(150)
        results_layout.addWidget(self.results_table)
        
        # Кнопки для результатов
        results_buttons = QHBoxLayout()
        self.save_results_btn = QPushButton("Сохранить выбранные результаты")
        self.save_results_btn.clicked.connect(self.on_save_results)
        self.save_results_btn.setEnabled(False)
        results_buttons.addWidget(self.save_results_btn)
        
        self.export_btn = QPushButton("Экспорт результатов")
        self.export_btn.clicked.connect(self.on_export_current)
        self.export_btn.setEnabled(False)
        results_buttons.addWidget(self.export_btn)
        
        results_layout.addLayout(results_buttons)
        
        main_layout.addWidget(results_group)
        
        # Индикатор загрузки (скрыт по умолчанию)
        self.loading_label = QLabel("Отправка запросов...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("color: blue; font-weight: bold;")
        self.loading_label.hide()
        main_layout.addWidget(self.loading_label)
    
    def load_prompts(self):
        """Загружает список сохраненных промтов в выпадающий список"""
        self.prompt_combo.clear()
        self.prompt_combo.addItem("-- Новый промт --", None)
        
        prompts = db.get_prompts()
        for prompt in prompts:
            prompt_text = prompt["prompt"][:50] + "..." if len(prompt["prompt"]) > 50 else prompt["prompt"]
            display_text = f"{prompt_text} ({prompt['date'][:10]})"
            self.prompt_combo.addItem(display_text, prompt["id"])
    
    def on_prompt_selected(self, index: int):
        """Обработчик выбора промта из списка"""
        if index > 0:  # Не первый элемент (-- Новый промт --)
            prompt_id = self.prompt_combo.itemData(index)
            if prompt_id:
                prompt_data = db.get_prompt_by_id(prompt_id)
                if prompt_data:
                    self.prompt_edit.setPlainText(prompt_data["prompt"])
    
    def on_select_prompt(self):
        """Обработчик кнопки 'Выбрать промт'"""
        index = self.prompt_combo.currentIndex()
        if index > 0:
            self.on_prompt_selected(index)
        else:
            QMessageBox.information(self, "Информация", "Выберите промт из списка")
    
    def on_save_prompt(self):
        """Обработчик кнопки 'Сохранить промт'"""
        prompt_text = self.prompt_edit.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите текст промта")
            return
        
        dialog = SavePromptDialog(prompt_text, self)
        if dialog.exec_() == QDialog.Accepted:
            tags = dialog.get_tags().strip()
            db.add_prompt(prompt_text, tags if tags else None)
            self.load_prompts()
            QMessageBox.information(self, "Успех", "Промт сохранен")
    
    def on_send_request(self):
        """Обработчик кнопки 'Отправить запрос'"""
        prompt_text = self.prompt_edit.toPlainText().strip()
        if not prompt_text:
            QMessageBox.warning(self, "Предупреждение", "Введите текст промта")
            return
        
        # Проверяем наличие активных моделей
        active_models = db.get_active_models()
        if not active_models:
            reply = QMessageBox.question(
                self, "Нет активных моделей",
                "В базе данных нет активных моделей.\n\n"
                "Хотите открыть окно управления моделями?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.on_manage_models()
            return
        
        # Очищаем временную таблицу результатов
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.save_results_btn.setEnabled(False)
        
        # Блокируем кнопку отправки
        self.send_btn.setEnabled(False)
        self.loading_label.show()
        
        # Создаем и запускаем поток для выполнения запросов
        self.worker_thread = WorkerThread(prompt_text)
        self.worker_thread.finished.connect(self.on_requests_finished)
        self.worker_thread.error.connect(self.on_requests_error)
        self.worker_thread.start()
    
    def on_requests_finished(self, results: List[models.ModelResult]):
        """Обработчик завершения запросов"""
        self.loading_label.hide()
        self.send_btn.setEnabled(True)
        
        # Сохраняем результаты во временную таблицу
        self.temp_results = [result.to_dict() for result in results]
        
        # Обновляем таблицу
        self.update_results_table()
        
        if results:
            self.save_results_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            success_count = sum(1 for r in results if "Ошибка" not in r.response)
            if success_count < len(results):
                QMessageBox.warning(
                    self, "Частичный успех", 
                    f"Получено ответов: {success_count} из {len(results)}. "
                    "Некоторые модели вернули ошибки."
                )
            else:
                QMessageBox.information(self, "Готово", f"Получено ответов: {len(results)}")
        else:
            QMessageBox.warning(self, "Предупреждение", "Не получено ни одного ответа")
    
    def on_requests_error(self, error_msg: str):
        """Обработчик ошибки при выполнении запросов"""
        self.loading_label.hide()
        self.send_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", f"Ошибка при отправке запросов: {error_msg}")
    
    def update_results_table(self):
        """Обновляет таблицу результатов"""
        self.results_table.setRowCount(len(self.temp_results))
        
        for row, result in enumerate(self.temp_results):
            # Чекбокс
            checkbox = QCheckBox()
            is_selected = result.get("selected", False)
            checkbox.setChecked(is_selected)
            # Используем замыкание для правильного захвата переменных
            def make_checkbox_handler(r, res):
                def handler(state):
                    res["selected"] = (state == Qt.Checked)
                return handler
            checkbox.stateChanged.connect(make_checkbox_handler(row, result))
            self.results_table.setCellWidget(row, 0, checkbox)
            
            # Название модели
            model_item = QTableWidgetItem(result.get("model_name", "Unknown"))
            model_item.setFlags(model_item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row, 1, model_item)
            
            # Ответ
            response_item = QTableWidgetItem(result.get("response", ""))
            response_item.setFlags(response_item.flags() & ~Qt.ItemIsEditable)
            response_item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)
            # Включаем перенос текста для многострочного отображения
            response_text = result.get("response", "")
            response_item.setData(Qt.UserRole, response_text)  # Сохраняем полный текст
            response_item.setToolTip(response_text)  # Полный текст в подсказке при наведении
            self.results_table.setItem(row, 2, response_item)
            
            # Кнопка "Открыть" для просмотра в markdown
            open_btn = QPushButton("Открыть")
            open_btn.clicked.connect(lambda checked, r=row: self.on_open_response(r))
            self.results_table.setCellWidget(row, 3, open_btn)
        
        # Настраиваем ширину колонок
        self.results_table.resizeColumnToContents(0)  # Чекбокс
        self.results_table.resizeColumnToContents(1)  # Название модели
        # Колонка с ответом уже настроена на Stretch
        
        # Автоматически подстраиваем высоту строк с учетом многострочного текста
        self.results_table.resizeRowsToContents()
        
        # Устанавливаем минимальную высоту строк для лучшей читаемости длинных ответов
        for row in range(self.results_table.rowCount()):
            current_height = self.results_table.rowHeight(row)
            # Минимальная высота 150px для комфортного чтения, но если текст длиннее - увеличиваем
            min_height = max(150, current_height)
            # Максимальная высота 500px, чтобы не было слишком длинных строк
            max_height = min(500, min_height)
            self.results_table.setRowHeight(row, max_height)
    
    def on_checkbox_changed(self, row: int, state: int, result: Dict = None):
        """Обработчик изменения состояния чекбокса"""
        is_checked = (state == Qt.Checked)
        if result:
            # Обновляем напрямую переданный результат
            result["selected"] = is_checked
        elif row < len(self.temp_results):
            # Обновляем по индексу
            self.temp_results[row]["selected"] = is_checked
    
    def on_save_results(self):
        """Обработчик кнопки 'Сохранить выбранные результаты'"""
        # Сначала обновляем состояние чекбоксов из таблицы
        for row in range(self.results_table.rowCount()):
            if row < len(self.temp_results):
                checkbox = self.results_table.cellWidget(row, 0)
                if checkbox:
                    self.temp_results[row]["selected"] = checkbox.isChecked()
        
        selected_results = [r for r in self.temp_results if r.get("selected", False)]
        
        if not selected_results:
            QMessageBox.warning(self, "Предупреждение", "Выберите хотя бы один результат для сохранения")
            return
        
        # Получаем текст промта
        prompt_text = self.prompt_edit.toPlainText().strip()
        
        # Сохраняем промт, если его еще нет в БД
        prompt_id = None
        if prompt_text:
            # Проверяем, есть ли уже такой промт
            existing_prompts = db.search_prompts(prompt_text, "prompt")
            if existing_prompts:
                prompt_id = existing_prompts[0]["id"]
            else:
                try:
                    prompt_id = db.add_prompt(prompt_text)
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт: {e}")
                    return
        
        # Сохраняем каждый выбранный результат
        saved_count = 0
        errors = []
        for result in selected_results:
            model_name = result.get("model_name", "")
            response_text = result.get("response", "")
            
            if not response_text:
                errors.append(f"Пустой ответ от модели {model_name}")
                continue
            
            # Находим ID модели по имени
            all_models = db.get_models()
            model_id = None
            for model in all_models:
                if model["name"] == model_name:
                    model_id = model["id"]
                    break
            
            if not model_id:
                errors.append(f"Модель '{model_name}' не найдена в базе данных")
                continue
            
            try:
                db.save_result(
                    prompt_id=prompt_id,
                    model_id=model_id,
                    response=response_text,
                    prompt_text=prompt_text
                )
                saved_count += 1
            except Exception as e:
                errors.append(f"Ошибка при сохранении результата от {model_name}: {e}")
        
        # Очищаем временную таблицу
        self.temp_results = []
        self.results_table.setRowCount(0)
        self.save_results_btn.setEnabled(False)
        
        # Показываем результат
        if errors:
            error_msg = f"Сохранено: {saved_count}\n\nОшибки:\n" + "\n".join(errors)
            QMessageBox.warning(self, "Частичный успех", error_msg)
        else:
            QMessageBox.information(self, "Успех", f"Сохранено результатов: {saved_count}")
    
    def on_manage_models(self):
        """Открывает диалог управления моделями"""
        try:
            dialog = ModelsDialog(self)
            dialog.exec_()
            # Обновляем список промтов на случай, если были изменения
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог управления моделями: {e}")
    
    def on_manage_prompts(self):
        """Открывает диалог управления промтами"""
        try:
            dialog = PromptsDialog(self)
            dialog.exec_()
            self.load_prompts()  # Обновляем список промтов
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог управления промтами: {e}")
    
    def on_view_results(self):
        """Открывает диалог просмотра результатов"""
        try:
            dialog = ResultsDialog(self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть диалог результатов: {e}")
    
    def on_export(self, format_type: str):
        """Экспорт текущих результатов в файл"""
        if not self.temp_results:
            QMessageBox.warning(self, "Предупреждение", "Нет результатов для экспорта")
            return
        
        # Фильтруем только выбранные результаты
        selected_results = [r for r in self.temp_results if r.get("selected", False)]
        if not selected_results:
            reply = QMessageBox.question(
                self, "Подтверждение",
                "Нет выбранных результатов. Экспортировать все?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                selected_results = self.temp_results
            else:
                return
        
        # Выбираем расширение файла
        extensions = {
            "markdown": "Markdown (*.md)",
            "json": "JSON (*.json)",
            "text": "Text (*.txt)"
        }
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты",
            "",
            extensions.get(format_type, "All Files (*)")
        )
        
        if not filename:
            return
        
        try:
            prompt_text = self.prompt_edit.toPlainText().strip()
            
            if format_type == "markdown":
                content = export.export_to_markdown(selected_results, prompt_text)
            elif format_type == "json":
                content = export.export_to_json(selected_results, prompt_text)
            else:  # text
                content = export.export_to_text(selected_results, prompt_text)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            QMessageBox.information(self, "Успех", f"Результаты экспортированы в {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать результаты: {e}")
    
    def on_export_current(self):
        """Экспорт текущих результатов (вызывает диалог выбора формата)"""
        if not self.temp_results:
            QMessageBox.warning(self, "Предупреждение", "Нет результатов для экспорта")
            return
        
        # Просто экспортируем в Markdown по умолчанию
        self.on_export("markdown")
    
    def on_open_response(self, row: int):
        """Открывает ответ модели в диалоге с форматированным markdown"""
        if row < 0 or row >= len(self.temp_results):
            return
        
        result = self.temp_results[row]
        model_name = result.get("model_name", "Unknown")
        response_text = result.get("response", "")
        
        if not response_text:
            QMessageBox.information(self, "Информация", "Ответ пуст")
            return
        
        # Открываем диалог с форматированным markdown
        dialog = MarkdownViewerDialog(model_name, response_text, self)
        dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
