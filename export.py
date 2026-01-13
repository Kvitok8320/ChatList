"""
Модуль для экспорта результатов в различные форматы
"""
import json
from datetime import datetime
from typing import List, Dict


def export_to_markdown(results: List[Dict], prompt_text: str = "") -> str:
    """
    Экспортирует результаты в формат Markdown
    
    Args:
        results: Список результатов для экспорта
        prompt_text: Текст промта
        
    Returns:
        Строка в формате Markdown
    """
    md = []
    md.append("# Результаты сравнения моделей\n")
    md.append(f"**Дата экспорта:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if prompt_text:
        md.append(f"## Промт\n\n{prompt_text}\n\n")
    
    md.append("## Результаты\n\n")
    
    for i, result in enumerate(results, 1):
        model_name = result.get("model_name", "Unknown")
        response = result.get("response", "")
        selected = result.get("selected", False)
        
        md.append(f"### {i}. {model_name}")
        if selected:
            md.append(" *(выбрано)*")
        md.append("\n\n")
        md.append(f"{response}\n\n")
        md.append("---\n\n")
    
    return "".join(md)


def export_to_json(results: List[Dict], prompt_text: str = "") -> str:
    """
    Экспортирует результаты в формат JSON
    
    Args:
        results: Список результатов для экспорта
        prompt_text: Текст промта
        
    Returns:
        Строка в формате JSON
    """
    data = {
        "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt_text,
        "results": results
    }
    
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_to_text(results: List[Dict], prompt_text: str = "") -> str:
    """
    Экспортирует результаты в простой текстовый формат
    
    Args:
        results: Список результатов для экспорта
        prompt_text: Текст промта
        
    Returns:
        Строка в текстовом формате
    """
    lines = []
    lines.append("=" * 80)
    lines.append("РЕЗУЛЬТАТЫ СРАВНЕНИЯ МОДЕЛЕЙ")
    lines.append("=" * 80)
    lines.append(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    if prompt_text:
        lines.append("ПРОМТ:")
        lines.append("-" * 80)
        lines.append(prompt_text)
        lines.append("")
    
    lines.append("РЕЗУЛЬТАТЫ:")
    lines.append("=" * 80)
    lines.append("")
    
    for i, result in enumerate(results, 1):
        model_name = result.get("model_name", "Unknown")
        response = result.get("response", "")
        selected = result.get("selected", False)
        
        lines.append(f"{i}. {model_name}" + (" [ВЫБРАНО]" if selected else ""))
        lines.append("-" * 80)
        lines.append(response)
        lines.append("")
        lines.append("=" * 80)
        lines.append("")
    
    return "\n".join(lines)


