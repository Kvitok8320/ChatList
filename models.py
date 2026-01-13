"""
Модуль для работы с моделями нейросетей
"""
from typing import List, Dict, Optional
from db import get_active_models
from network import send_request


class ModelResult:
    """Класс для представления результата запроса к модели"""
    def __init__(self, model_name: str, response: str, selected: bool = False):
        self.model_name = model_name
        self.response = response
        self.selected = selected
    
    def to_dict(self) -> Dict:
        """Преобразует объект в словарь"""
        return {
            "model_name": self.model_name,
            "response": self.response,
            "selected": self.selected
        }


def get_active_models_list() -> List[Dict]:
    """
    Получает список активных моделей из базы данных
    
    Returns:
        Список словарей с информацией о моделях
    """
    return get_active_models()


def send_prompt_to_models(prompt: str, model_ids: Optional[List[int]] = None) -> List[ModelResult]:
    """
    Отправляет промт во все активные модели (или указанные модели)
    
    Args:
        prompt: Текст промта
        model_ids: Список ID моделей для отправки (если None, то все активные)
        
    Returns:
        Список объектов ModelResult с результатами запросов
    """
    results = []
    
    # Получаем список моделей
    if model_ids:
        from db import get_model_by_id
        models = [get_model_by_id(mid) for mid in model_ids if get_model_by_id(mid)]
    else:
        models = get_active_models()
    
    if not models:
        return results
    
    # Отправляем запрос к каждой модели
    for model in models:
        model_name = model.get("name", "Unknown")
        try:
            response = send_request(model, prompt)
            if response:
                results.append(ModelResult(model_name, response, False))
            else:
                # Если запрос не удался, добавляем результат с сообщением об ошибке
                results.append(ModelResult(
                    model_name, 
                    "Ошибка: не удалось получить ответ от модели", 
                    False
                ))
        except Exception as e:
            results.append(ModelResult(
                model_name,
                f"Ошибка: {str(e)}",
                False
            ))
    
    return results


def process_results(results: List[ModelResult]) -> List[Dict]:
    """
    Обрабатывает результаты запросов и преобразует их в список словарей
    
    Args:
        results: Список объектов ModelResult
        
    Returns:
        Список словарей с результатами
    """
    return [result.to_dict() for result in results]




