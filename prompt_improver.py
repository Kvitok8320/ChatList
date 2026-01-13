"""
Модуль для улучшения промтов с помощью AI
"""
import json
import re
from typing import Dict, List, Optional
from network import send_request
from db import get_active_models, get_model_by_id


# Промпты-шаблоны для улучшения
IMPROVEMENT_PROMPT = """Ты - эксперт по формулировке промптов для AI-моделей. 

Исходный промпт пользователя:
"{original_prompt}"

Задача:
1. Улучши этот промпт, сделав его более четким, конкретным и эффективным
2. Предложи 2-3 альтернативных варианта переформулировки
3. Если возможно, адаптируй промпт для разных типов задач (технические, аналитические, креативные)

Верни ответ в формате JSON:
{{
    "improved": "улучшенная версия промпта",
    "alternatives": ["вариант 1", "вариант 2", "вариант 3"],
    "technical": "версия для технических задач (если применимо)",
    "analytical": "версия для аналитических задач (если применимо)",
    "creative": "версия для креативных задач (если применимо)"
}}

Если какой-то вариант не применим, верни null для этого поля."""

TECHNICAL_ADAPTATION_PROMPT = """Переформулируй следующий промпт для технической задачи или программирования. Сделай его более точным и структурированным:

"{original_prompt}"

Верни только улучшенный промпт без дополнительных пояснений."""

ANALYTICAL_ADAPTATION_PROMPT = """Адаптируй следующий промпт для аналитической задачи или исследования. Добавь структуру и четкие критерии оценки:

"{original_prompt}"

Верни только улучшенный промпт без дополнительных пояснений."""

CREATIVE_ADAPTATION_PROMPT = """Переформулируй следующий промпт для творческой задачи. Сделай его более вдохновляющим и открытым для креативных решений:

"{original_prompt}"

Верни только улучшенный промпт без дополнительных пояснений."""


def parse_improvement_response(response_text: str) -> Dict:
    """
    Парсит ответ модели и извлекает улучшенные варианты промта
    
    Args:
        response_text: Текст ответа от модели
        
    Returns:
        Словарь с улучшенными вариантами промта
    """
    result = {
        "improved": "",
        "alternatives": [],
        "technical": None,
        "analytical": None,
        "creative": None
    }
    
    # Пытаемся извлечь JSON из ответа
    try:
        # Ищем JSON в тексте (может быть обернут в markdown код блоки)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Пытаемся найти JSON напрямую
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text
        
        data = json.loads(json_str)
        
        result["improved"] = data.get("improved", "")
        result["alternatives"] = data.get("alternatives", [])
        result["technical"] = data.get("technical")
        result["analytical"] = data.get("analytical")
        result["creative"] = data.get("creative")
        
    except (json.JSONDecodeError, AttributeError):
        # Если не удалось распарсить JSON, пытаемся извлечь информацию из текста
        lines = response_text.split('\n')
        
        # Ищем улучшенную версию
        improved_found = False
        current_section = None
        alternatives = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ищем заголовки
            if any(keyword in line.lower() for keyword in ["улучшен", "improved", "рекомендуем"]):
                improved_found = True
                current_section = "improved"
                continue
            elif any(keyword in line.lower() for keyword in ["альтернатив", "вариант", "alternative"]):
                current_section = "alternatives"
                continue
            elif "техническ" in line.lower() or "technical" in line.lower():
                current_section = "technical"
                continue
            elif "аналитическ" in line.lower() or "analytical" in line.lower():
                current_section = "analytical"
                continue
            elif "креатив" in line.lower() or "creative" in line.lower():
                current_section = "creative"
                continue
            
            # Извлекаем текст
            if improved_found and not result["improved"]:
                # Убираем маркеры списка
                clean_line = re.sub(r'^[-*•\d.]+\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    result["improved"] = clean_line
            elif current_section == "alternatives":
                clean_line = re.sub(r'^[-*•\d.]+\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    alternatives.append(clean_line)
            elif current_section == "technical" and not result["technical"]:
                clean_line = re.sub(r'^[-*•\d.]+\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    result["technical"] = clean_line
            elif current_section == "analytical" and not result["analytical"]:
                clean_line = re.sub(r'^[-*•\d.]+\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    result["analytical"] = clean_line
            elif current_section == "creative" and not result["creative"]:
                clean_line = re.sub(r'^[-*•\d.]+\s*', '', line)
                if clean_line and len(clean_line) > 10:
                    result["creative"] = clean_line
        
        result["alternatives"] = alternatives[:3]  # Ограничиваем 3 вариантами
        
        # Если не нашли улучшенную версию, используем весь ответ
        if not result["improved"] and response_text:
            result["improved"] = response_text[:500]  # Берем первые 500 символов
    
    return result


def improve_prompt(original_prompt: str, model_id: Optional[int] = None) -> Dict:
    """
    Улучшает промт с помощью выбранной модели
    
    Args:
        original_prompt: Исходный промт для улучшения
        model_id: ID модели для улучшения (если None, берется первая активная)
        
    Returns:
        Словарь с улучшенными вариантами промта
    """
    if not original_prompt or not original_prompt.strip():
        return {
            "improved": "",
            "alternatives": [],
            "technical": None,
            "analytical": None,
            "creative": None,
            "error": "Промт не может быть пустым"
        }
    
    # Получаем модель для улучшения
    if model_id:
        model = get_model_by_id(model_id)
    else:
        active_models = get_active_models()
        if not active_models:
            return {
                "improved": "",
                "alternatives": [],
                "technical": None,
                "analytical": None,
                "creative": None,
                "error": "Нет активных моделей"
            }
        model = active_models[0]  # Берем первую активную модель
    
    if not model:
        return {
            "improved": "",
            "alternatives": [],
            "technical": None,
            "analytical": None,
            "creative": None,
            "error": "Модель не найдена"
        }
    
    # Формируем промпт для улучшения
    improvement_prompt = IMPROVEMENT_PROMPT.format(original_prompt=original_prompt)
    
    # Отправляем запрос
    try:
        response = send_request(model, improvement_prompt)
        
        if not response or response.startswith("Ошибка:"):
            return {
                "improved": "",
                "alternatives": [],
                "technical": None,
                "analytical": None,
                "creative": None,
                "error": response or "Не удалось получить ответ от модели"
            }
        
        # Парсим ответ
        result = parse_improvement_response(response)
        result["model_name"] = model.get("name", "Unknown")
        
        return result
        
    except Exception as e:
        return {
            "improved": "",
            "alternatives": [],
            "technical": None,
            "analytical": None,
            "creative": None,
            "error": f"Ошибка при улучшении промта: {str(e)}"
        }


def adapt_prompt_for_type(original_prompt: str, adaptation_type: str, model_id: Optional[int] = None) -> str:
    """
    Адаптирует промт для конкретного типа задачи
    
    Args:
        original_prompt: Исходный промт
        adaptation_type: Тип адаптации ("technical", "analytical", "creative")
        model_id: ID модели (если None, берется первая активная)
        
    Returns:
        Адаптированный промт
    """
    if not original_prompt or not original_prompt.strip():
        return ""
    
    # Выбираем шаблон
    if adaptation_type == "technical":
        template = TECHNICAL_ADAPTATION_PROMPT
    elif adaptation_type == "analytical":
        template = ANALYTICAL_ADAPTATION_PROMPT
    elif adaptation_type == "creative":
        template = CREATIVE_ADAPTATION_PROMPT
    else:
        return original_prompt
    
    adaptation_prompt = template.format(original_prompt=original_prompt)
    
    # Получаем модель
    if model_id:
        model = get_model_by_id(model_id)
    else:
        active_models = get_active_models()
        if not active_models:
            return original_prompt
        model = active_models[0]
    
    if not model:
        return original_prompt
    
    # Отправляем запрос
    try:
        response = send_request(model, adaptation_prompt)
        if response and not response.startswith("Ошибка:"):
            return response.strip()
        else:
            return original_prompt
    except Exception:
        return original_prompt

