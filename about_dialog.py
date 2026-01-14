"""
Диалог "О программе"
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
import sys
import os
from version import __version__


class AboutDialog(QDialog):
    """Диалог с информацией о программе"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Название программы
        title_label = QLabel("ChatList")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Версия
        version_label = QLabel(f"Версия {__version__}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        layout.addSpacing(20)
        
        # Описание программы
        description = QTextEdit()
        description.setReadOnly(True)
        description_text = """
<h3>Описание</h3>
<p>ChatList — это Python-приложение, которое позволяет отправлять один и тот же промт в несколько нейросетей и сравнивать их ответы.</p>

<h3>Основные возможности</h3>
<ul>
<li>Отправка промта в несколько AI-моделей одновременно</li>
<li>Сравнение ответов в удобной таблице</li>
<li>Сохранение промтов и результатов</li>
<li>Управление моделями и настройками</li>
<li>Экспорт результатов в различные форматы</li>
<li>AI-ассистент для улучшения промтов</li>
</ul>

<h3>Технологии</h3>
<ul>
<li>Python 3.11+</li>
<li>PyQt5 — графический интерфейс</li>
<li>SQLite — база данных</li>
<li>Requests — HTTP-запросы</li>
</ul>

<h3>Поддерживаемые API</h3>
<ul>
<li>OpenAI</li>
<li>DeepSeek</li>
<li>Groq</li>
<li>OpenRouter</li>
</ul>

<h3>Автор</h3>
<p>Разработано для удобного сравнения ответов различных AI-моделей.</p>
        """
        description.setHtml(description_text)
        description.setMaximumHeight(300)
        layout.addWidget(description)
        
        # Кнопка закрытия
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

