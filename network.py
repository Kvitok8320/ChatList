"""
Модуль для отправки HTTP-запросов к API нейросетей
"""
import os
import requests
import logging
from typing import Dict, Optional
from dotenv import load_dotenv
from version import __version__

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=f'%(asctime)s - ChatList v{__version__} - %(name)s - %(levelname)s - %(message)s',
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
        return None
    
    # Убираем пробелы и проверяем формат
    api_key = api_key.strip()
    if not api_key or api_key == f"your_{env_var_name.lower()}_here":
        logger.warning(f"API ключ {env_var_name} пустой или содержит placeholder")
        return None
    
    # Проверка формата OpenRouter ключа
    if env_var_name == "OPENROUTER_API_KEY" and not api_key.startswith("sk-or-v1-"):
        logger.warning(f"OpenRouter API ключ должен начинаться с 'sk-or-v1-'. Текущий ключ: {api_key[:10]}...")
    
    return api_key


def get_timeout() -> int:
    """Получает таймаут для запросов из настроек (по умолчанию 30 секунд)"""
    try:
        import db
        timeout_str = db.get_setting("timeout", "30")
        return int(timeout_str)
    except Exception:
        return 30


def get_proxies():
    """
    Получает настройки прокси из переменных окружения
    Если переменные не установлены, отключает прокси
    """
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
    https_proxy = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
    
    if http_proxy or https_proxy:
        proxies = {}
        if http_proxy:
            proxies["http"] = http_proxy
        if https_proxy:
            proxies["https"] = https_proxy
        return proxies
    else:
        # Отключаем прокси, если не указаны явно
        return {"http": None, "https": None}


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
            timeout=get_timeout(),
            proxies=get_proxies()
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
            timeout=get_timeout(),
            proxies=get_proxies()
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
            timeout=get_timeout(),
            proxies=get_proxies()
        )
        response.raise_for_status()
        
        # Проверяем Content-Type ответа
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            error_msg = f"Модель {model_id}: Сервер вернул HTML вместо JSON. " \
                       f"Возможно, прокси блокирует эту модель или модель недоступна. " \
                       f"Попробуйте другую модель или проверьте настройки прокси."
            logger.error(f"OpenRouter API вернул HTML для модели {model_id}")
            logger.error(f"Content-Type: {content_type}")
            logger.error(f"HTML ответ (первые 300 символов): {response.text[:300]}")
            return f"Ошибка: {error_msg}"
        
        # Проверяем, что ответ не пустой
        if not response.text:
            error_msg = "Пустой ответ от OpenRouter API"
            logger.error(error_msg)
            return f"Ошибка: {error_msg}"
        
        try:
            result = response.json()
        except ValueError as e:
            # Если получили HTML вместо JSON, это может быть страница ошибки от прокси или сервера
            response_text = response.text[:500]
            if "<!DOCTYPE html>" in response_text or "<html" in response_text.lower():
                error_msg = f"Модель {model_id}: Сервер вернул HTML вместо JSON. " \
                           f"Возможные причины: прокси блокирует запрос, модель недоступна, " \
                           f"или требуется специальный доступ. Попробуйте другую модель."
                logger.error(f"OpenRouter API вернул HTML вместо JSON для модели {model_id}")
                logger.error(f"HTML ответ (первые 200 символов): {response_text[:200]}")
            else:
                error_msg = f"Ошибка парсинга JSON от OpenRouter API для модели {model_id}: {str(e)}. " \
                           f"Ответ: {response_text[:200]}"
                logger.error(error_msg)
            return f"Ошибка: {error_msg}"
        
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]["content"]
            logger.info(f"Получен ответ от OpenRouter API: {len(message)} символов")
            return message
        elif "error" in result:
            error_msg = f"Ошибка от OpenRouter API: {result.get('error', {}).get('message', 'Неизвестная ошибка')}"
            logger.error(error_msg)
            return f"Ошибка: {error_msg}"
        else:
            error_msg = "Неожиданный формат ответа от OpenRouter API"
            logger.error(f"{error_msg}. Ответ: {response.text[:200]}")
            return f"Ошибка: {error_msg}"
            
    except requests.exceptions.Timeout:
        error_msg = f"Таймаут при запросе к OpenRouter API (модель: {model_id})"
        logger.error(error_msg)
        return f"Ошибка: {error_msg}"
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else "unknown"
        response_text = ""
        error_msg = ""
        
        if e.response:
            try:
                # Пытаемся получить JSON ошибки
                error_json = e.response.json()
                if "error" in error_json:
                    error_msg = error_json["error"].get("message", "Неизвестная ошибка")
                else:
                    error_msg = str(error_json)
            except:
                # Если не JSON (например, HTML страница ошибки), обрабатываем по статус коду
                response_text = e.response.text[:200]
                if status_code == 403:
                    error_msg = "403 Forbidden: Проверьте API ключ OpenRouter и права доступа. Убедитесь, что ключ правильный и начинается с 'sk-or-v1-'"
                elif status_code == 401:
                    error_msg = "401 Unauthorized: Неверный API ключ OpenRouter. Проверьте ключ в файле .env"
                elif status_code == 429:
                    error_msg = "429 Too Many Requests: Превышен лимит запросов. Попробуйте позже"
                elif status_code == 400:
                    error_msg = "400 Bad Request: Неверный формат запроса или модель недоступна"
                else:
                    error_msg = f"HTTP ошибка {status_code}"
        else:
            error_msg = f"HTTP ошибка {status_code}"
        
        full_error = f"{error_msg}" + (f" (ответ: {response_text[:100]})" if response_text else "")
        logger.error(f"Ошибка при запросе к OpenRouter API: {full_error}")
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
            timeout=get_timeout(),
            proxies=get_proxies()
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
    
    # Автоматическое определение типа API по URL, если тип не указан или неправильный
    if "openrouter.ai" in api_url.lower():
        logger.info(f"Автоопределение: используем OpenRouter API для {api_id}")
        return send_openrouter_request(api_url, api_key, api_id, prompt)
    elif "deepseek.com" in api_url.lower():
        logger.info(f"Автоопределение: используем DeepSeek API для {api_id}")
        return send_deepseek_request(api_url, api_key, api_id, prompt)
    elif "groq.com" in api_url.lower():
        logger.info(f"Автоопределение: используем Groq API для {api_id}")
        return send_groq_request(api_url, api_key, api_id, prompt)
    
    # Определение по явно указанному типу
    if model_type == "openai":
        return send_openai_request(api_url, api_key, api_id, prompt)
    elif model_type == "deepseek":
        return send_deepseek_request(api_url, api_key, api_id, prompt)
    elif model_type == "groq":
        return send_groq_request(api_url, api_key, api_id, prompt)
    elif model_type == "openrouter":
        return send_openrouter_request(api_url, api_key, api_id, prompt)
    else:
        logger.warning(f"Неизвестный тип модели: {model_type}, пытаемся OpenAI-совместимый формат")
        # Попробуем использовать OpenAI-совместимый формат
        return send_openai_request(api_url, api_key, api_id, prompt)

