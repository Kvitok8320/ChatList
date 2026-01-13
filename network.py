"""
Модуль для отправки HTTP-запросов к API нейросетей
"""
import os
import requests
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatlist.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_api_key(env_var_name: str) -> Optional[str]:
    """Получает API-ключ из переменной окружения"""
    api_key = os.getenv(env_var_name)
    if not api_key:
        logger.warning(f"API ключ {env_var_name} не найден в переменных окружения")
    return api_key


def get_timeout() -> int:
    """Получает таймаут для запросов из настроек (по умолчанию 30 секунд)"""
    try:
        import db
        timeout_str = db.get_setting("timeout", "30")
        return int(timeout_str)
    except Exception:
        return 30


def send_openai_request(api_url: str, api_key: str, model_id: str, prompt: str) -> Optional[str]:
    """
    Отправляет запрос к OpenAI API
    
    Args:
        api_url: URL API
        api_key: API ключ
        model_id: ID модели
        prompt: Текст промта
        
    Returns:
        Ответ модели или None в случае ошибки
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        logger.info(f"Отправка запроса к OpenAI API: модель {model_id}")
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=get_timeout()
        )
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            logger.info(f"Получен ответ от OpenAI API: {len(message)} символов")
            return message
        else:
            logger.error("Неожиданный формат ответа от OpenAI API")
            return None
            
    except requests.exceptions.Timeout:
        error_msg = f"Таймаут при запросе к OpenAI API (модель: {model_id})"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP ошибка {e.response.status_code}: {e.response.text[:200] if e.response else str(e)}"
        logger.error(f"Ошибка при запросе к OpenAI API: {error_msg}")
        return f"Ошибка: {error_msg}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сети при запросе к OpenAI API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except Exception as e:
        error_msg = f"Неожиданная ошибка при запросе к OpenAI API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"


def send_deepseek_request(api_url: str, api_key: str, model_id: str, prompt: str) -> Optional[str]:
    """
    Отправляет запрос к DeepSeek API
    
    Args:
        api_url: URL API
        api_key: API ключ
        model_id: ID модели
        prompt: Текст промта
        
    Returns:
        Ответ модели или None в случае ошибки
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        logger.info(f"Отправка запроса к DeepSeek API: модель {model_id}")
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=get_timeout()
        )
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            logger.info(f"Получен ответ от DeepSeek API: {len(message)} символов")
            return message
        else:
            logger.error("Неожиданный формат ответа от DeepSeek API")
            return None
            
    except requests.exceptions.Timeout:
        error_msg = f"Таймаут при запросе к DeepSeek API (модель: {model_id})"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP ошибка {e.response.status_code}: {e.response.text[:200] if e.response else str(e)}"
        logger.error(f"Ошибка при запросе к DeepSeek API: {error_msg}")
        return f"Ошибка: {error_msg}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сети при запросе к DeepSeek API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except Exception as e:
        error_msg = f"Неожиданная ошибка при запросе к DeepSeek API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"


def send_openrouter_request(api_url: str, api_key: str, model_id: str, prompt: str) -> Optional[str]:
    """
    Отправляет запрос к OpenRouter API
    
    Args:
        api_url: URL API
        api_key: API ключ
        model_id: ID модели
        prompt: Текст промта
        
    Returns:
        Ответ модели или None в случае ошибки
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/chatlist",
            "X-Title": "ChatList"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        logger.info(f"Отправка запроса к OpenRouter API: модель {model_id}")
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=get_timeout()
        )
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            logger.info(f"Получен ответ от OpenRouter API: {len(message)} символов")
            return message
        else:
            logger.error("Неожиданный формат ответа от OpenRouter API")
            return None
            
    except requests.exceptions.Timeout:
        error_msg = f"Таймаут при запросе к OpenRouter API (модель: {model_id})"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP ошибка {e.response.status_code}: {e.response.text[:200] if e.response else str(e)}"
        logger.error(f"Ошибка при запросе к OpenRouter API: {error_msg}")
        return f"Ошибка: {error_msg}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сети при запросе к OpenRouter API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except Exception as e:
        error_msg = f"Неожиданная ошибка при запросе к OpenRouter API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"


def send_groq_request(api_url: str, api_key: str, model_id: str, prompt: str) -> Optional[str]:
    """
    Отправляет запрос к Groq API
    
    Args:
        api_url: URL API
        api_key: API ключ
        model_id: ID модели
        prompt: Текст промта
        
    Returns:
        Ответ модели или None в случае ошибки
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        logger.info(f"Отправка запроса к Groq API: модель {model_id}")
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=get_timeout()
        )
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            logger.info(f"Получен ответ от Groq API: {len(message)} символов")
            return message
        else:
            logger.error("Неожиданный формат ответа от Groq API")
            return None
            
    except requests.exceptions.Timeout:
        error_msg = f"Таймаут при запросе к Groq API (модель: {model_id})"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP ошибка {e.response.status_code}: {e.response.text[:200] if e.response else str(e)}"
        logger.error(f"Ошибка при запросе к Groq API: {error_msg}")
        return f"Ошибка: {error_msg}"
    except requests.exceptions.RequestException as e:
        error_msg = f"Ошибка сети при запросе к Groq API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except Exception as e:
        error_msg = f"Неожиданная ошибка при запросе к Groq API: {str(e)}"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"


def send_request(model_info: Dict, prompt: str) -> Optional[str]:
    """
    Универсальная функция для отправки запроса к API
    
    Определяет тип API по полю model_type и вызывает соответствующую функцию
    
    Args:
        model_info: Словарь с информацией о модели из БД
        prompt: Текст промта
        
    Returns:
        Ответ модели или None в случае ошибки
    """
    api_key_env = model_info.get("api_key_env")
    api_url = model_info.get("api_url")
    api_id = model_info.get("api_id")
    model_type = model_info.get("model_type", "").lower()
    
    if not api_key_env or not api_url or not api_id:
        logger.error("Неполная информация о модели")
        return None
    
    api_key = get_api_key(api_key_env)
    if not api_key:
        logger.error(f"API ключ не найден: {api_key_env}")
        return None
    
    if model_type == "openai":
        return send_openai_request(api_url, api_key, api_id, prompt)
    elif model_type == "deepseek":
        return send_deepseek_request(api_url, api_key, api_id, prompt)
    elif model_type == "groq":
        return send_groq_request(api_url, api_key, api_id, prompt)
    elif model_type == "openrouter":
        return send_openrouter_request(api_url, api_key, api_id, prompt)
    else:
        logger.error(f"Неизвестный тип модели: {model_type}")
        # Попробуем использовать OpenAI-совместимый формат
        return send_openai_request(api_url, api_key, api_id, prompt)

