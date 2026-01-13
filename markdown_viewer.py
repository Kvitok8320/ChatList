"""
Диалог для просмотра ответа в формате Markdown
"""
import re
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


def markdown_to_html(markdown_text: str) -> str:
    """
    Простая конвертация Markdown в HTML для отображения в QTextEdit
    """
    html = markdown_text
    
    # Заголовки
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Жирный текст
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
    
    # Курсив
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
    
    # Код (inline)
    html = re.sub(r'`([^`]+)`', r'<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">\1</code>', html)
    
    # Код (блоки)
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto;"><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Ссылки
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Списки (нумерованные)
    lines = html.split('\n')
    in_list = False
    result_lines = []
    for line in lines:
        if re.match(r'^\d+\.\s', line):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
            content = re.sub(r'^\d+\.\s', '', line)
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                result_lines.append('</ol>')
                in_list = False
            result_lines.append(line)
    if in_list:
        result_lines.append('</ol>')
    html = '\n'.join(result_lines)
    
    # Списки (маркированные)
    lines = html.split('\n')
    in_list = False
    result_lines = []
    for line in lines:
        if re.match(r'^[-*+]\s', line):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            content = re.sub(r'^[-*+]\s', '', line)
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            result_lines.append(line)
    if in_list:
        result_lines.append('</ul>')
    html = '\n'.join(result_lines)
    
    # Горизонтальная линия
    html = re.sub(r'^---$', r'<hr>', html, flags=re.MULTILINE)
    html = re.sub(r'^\*\*\*$', r'<hr>', html, flags=re.MULTILINE)
    
    # Параграфы (заменяем двойные переносы строк на </p><p>)
    html = re.sub(r'\n\n+', r'</p><p>', html)
    html = '<p>' + html + '</p>'
    
    # Очищаем пустые параграфы
    html = re.sub(r'<p>\s*</p>', '', html)
    
    # Базовый стиль
    style = """
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
        h1 { color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; }
        h2 { color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 20px; }
        h3 { color: #777; margin-top: 15px; }
        code { font-family: 'Courier New', monospace; }
        pre { background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        ul, ol { margin-left: 20px; }
        li { margin: 5px 0; }
        hr { border: none; border-top: 1px solid #ddd; margin: 20px 0; }
    </style>
    """
    
    return f"<html><head>{style}</head><body>{html}</body></html>"


class MarkdownViewerDialog(QDialog):
    """Диалог для просмотра ответа в формате Markdown"""
    def __init__(self, model_name: str, response_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ответ: {model_name}")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Заголовок с названием модели
        header = QLabel(f"<h2>{model_name}</h2>")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Текстовое поле для отображения markdown
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        self.text_view.setFont(QFont("Arial", 10))
        
        # Конвертируем markdown в HTML и отображаем
        html_content = markdown_to_html(response_text)
        self.text_view.setHtml(html_content)
        
        layout.addWidget(self.text_view)
        
        # Кнопка закрытия
        buttons = QHBoxLayout()
        buttons.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)

