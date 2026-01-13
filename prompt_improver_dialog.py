"""
Диалог для отображения результатов улучшения промта
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QGroupBox, QScrollArea, QWidget, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from typing import Dict, Optional
import db


class PromptImproverDialog(QDialog):
    """Диалог для отображения результатов улучшения промта"""
    def __init__(self, original_prompt: str, improvement_result: Dict, parent=None):
        super().__init__(parent)
        self.original_prompt = original_prompt
        self.improvement_result = improvement_result
        self.selected_prompt = None
        
        self.setWindowTitle("Улучшение промта")
        self.setMinimumSize(900, 700)
        
        layout = QVBoxLayout()
        
        # Исходный промт
        original_group = QGroupBox("Исходный промт")
        original_layout = QVBoxLayout()
        self.original_text = QTextEdit()
        self.original_text.setPlainText(original_prompt)
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(100)
        original_layout.addWidget(self.original_text)
        original_group.setLayout(original_layout)
        layout.addWidget(original_group)
        
        # Улучшенный промт
        improved_group = QGroupBox("Улучшенный промт")
        improved_layout = QVBoxLayout()
        self.improved_text = QTextEdit()
        improved_prompt = improvement_result.get("improved", "")
        if not improved_prompt and "error" in improvement_result:
            improved_prompt = f"Ошибка: {improvement_result['error']}"
        self.improved_text.setPlainText(improved_prompt)
        self.improved_text.setMaximumHeight(120)
        improved_layout.addWidget(self.improved_text)
        
        use_improved_btn = QPushButton("Использовать улучшенный промт")
        use_improved_btn.clicked.connect(lambda: self.on_use_prompt(improved_prompt))
        improved_layout.addWidget(use_improved_btn)
        improved_group.setLayout(improved_layout)
        layout.addWidget(improved_group)
        
        # Альтернативные варианты
        alternatives = improvement_result.get("alternatives", [])
        if alternatives:
            alternatives_group = QGroupBox(f"Альтернативные варианты ({len(alternatives)})")
            alternatives_layout = QVBoxLayout()
            
            for idx, alt in enumerate(alternatives, 1):
                alt_widget = QWidget()
                alt_layout = QVBoxLayout()
                alt_widget.setLayout(alt_layout)
                
                alt_text = QTextEdit()
                alt_text.setPlainText(alt)
                alt_text.setMaximumHeight(100)
                alt_text.setReadOnly(True)
                alt_layout.addWidget(alt_text)
                
                use_alt_btn = QPushButton(f"Использовать вариант {idx}")
                use_alt_btn.clicked.connect(lambda checked, prompt=alt: self.on_use_prompt(prompt))
                alt_layout.addWidget(use_alt_btn)
                
                alternatives_layout.addWidget(alt_widget)
            
            alternatives_group.setLayout(alternatives_layout)
            layout.addWidget(alternatives_group)
        
        # Адаптированные версии
        adaptations_layout = QHBoxLayout()
        
        technical = improvement_result.get("technical")
        if technical:
            tech_group = QGroupBox("Для технических задач")
            tech_layout = QVBoxLayout()
            tech_text = QTextEdit()
            tech_text.setPlainText(technical)
            tech_text.setMaximumHeight(100)
            tech_text.setReadOnly(True)
            tech_layout.addWidget(tech_text)
            use_tech_btn = QPushButton("Использовать")
            use_tech_btn.clicked.connect(lambda: self.on_use_prompt(technical))
            tech_layout.addWidget(use_tech_btn)
            tech_group.setLayout(tech_layout)
            adaptations_layout.addWidget(tech_group)
        
        analytical = improvement_result.get("analytical")
        if analytical:
            anal_group = QGroupBox("Для аналитических задач")
            anal_layout = QVBoxLayout()
            anal_text = QTextEdit()
            anal_text.setPlainText(analytical)
            anal_text.setMaximumHeight(100)
            anal_text.setReadOnly(True)
            anal_layout.addWidget(anal_text)
            use_anal_btn = QPushButton("Использовать")
            use_anal_btn.clicked.connect(lambda: self.on_use_prompt(analytical))
            anal_layout.addWidget(use_anal_btn)
            anal_group.setLayout(anal_layout)
            adaptations_layout.addWidget(anal_group)
        
        creative = improvement_result.get("creative")
        if creative:
            creat_group = QGroupBox("Для креативных задач")
            creat_layout = QVBoxLayout()
            creat_text = QTextEdit()
            creat_text.setPlainText(creative)
            creat_text.setMaximumHeight(100)
            creat_text.setReadOnly(True)
            creat_layout.addWidget(creat_text)
            use_creat_btn = QPushButton("Использовать")
            use_creat_btn.clicked.connect(lambda: self.on_use_prompt(creative))
            creat_layout.addWidget(use_creat_btn)
            creat_group.setLayout(creat_layout)
            adaptations_layout.addWidget(creat_group)
        
        if technical or analytical or creative:
            adaptations_group = QGroupBox("Адаптированные версии")
            adaptations_group.setLayout(adaptations_layout)
            layout.addWidget(adaptations_group)
        
        # Информация о модели
        model_name = improvement_result.get("model_name", "Unknown")
        info_label = QLabel(f"Улучшено с помощью: {model_name}")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        # Поле для тегов при сохранении
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Теги (через запятую)")
        buttons_layout.addWidget(QLabel("Теги:"))
        buttons_layout.addWidget(self.tags_input)
        
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Сохранить улучшенный промт")
        save_btn.clicked.connect(self.on_save_prompt)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Закрыть")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def on_use_prompt(self, prompt: str):
        """Обработчик использования промта"""
        self.selected_prompt = prompt
        self.accept()
    
    def on_save_prompt(self):
        """Сохранение улучшенного промта"""
        improved = self.improved_text.toPlainText().strip()
        if not improved:
            QMessageBox.warning(self, "Предупреждение", "Нет улучшенного промта для сохранения")
            return
        
        # Получаем теги
        tags_text = self.tags_input.text().strip()
        tags = ", ".join([tag.strip() for tag in tags_text.split(",") if tag.strip()]) if tags_text else None
        
        # Сохраняем в базу данных
        try:
            db.add_prompt(improved, tags)
            QMessageBox.information(self, "Успех", "Промт сохранен в базу данных")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить промт: {e}")
        
        self.selected_prompt = improved
        self.accept()
    
    def get_selected_prompt(self) -> Optional[str]:
        """Возвращает выбранный промт"""
        return self.selected_prompt

