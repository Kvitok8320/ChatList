# -*- coding: utf-8 -*-
"""Простой скрипт для проверки OpenRouter API ключа"""
import os
import requests
from dotenv import load_dotenv

print("=" * 60)
print("Проверка OpenRouter API ключа")
print("=" * 60)
print()

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("ОШИБКА: OPENROUTER_API_KEY не найден в .env файле")
    print("Убедитесь, что файл .env существует и содержит OPENROUTER_API_KEY")
    input("Нажмите Enter для выхода...")
    exit(1)

api_key = api_key.strip()

print("API ключ найден")
print("Начало ключа:", api_key[:15] + "...")
print("Конец ключа: ..." + api_key[-10:])
print("Длина ключа:", len(api_key), "символов")

# Проверка формата
if not api_key.startswith("sk-or-v1-"):
    print()
    print("ПРЕДУПРЕЖДЕНИЕ: Ключ не начинается с 'sk-or-v1-'")
    print("Это может быть неверный формат ключа OpenRouter")
else:
    print("Формат ключа правильный (начинается с 'sk-or-v1-')")

print()
print("Отправка тестового запроса к OpenRouter API...")
print()

# Тестируем запрос
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/chatlist",
    "X-Title": "ChatList"
}

data = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Привет! Ответь одним словом: работает?"}
    ]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print("Статус код:", response.status_code)
    print()
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result:
            message = result["choices"][0]["message"]["content"]
            print("УСПЕХ! API ключ работает правильно!")
            print("Ответ модели:", message)
        else:
            print("ОШИБКА: Неожиданный формат ответа")
            print("Ответ:", result)
    elif response.status_code == 403:
        print("ОШИБКА 403 Forbidden")
        print("Проблема с API ключом или правами доступа")
        print()
        print("Возможные причины:")
        print("1. API ключ неверный или истек")
        print("2. Недостаточно прав доступа")
        print("3. Ключ заблокирован")
        print()
        try:
            error_json = response.json()
            print("Детали ошибки:", error_json)
        except:
            print("Ответ сервера (первые 300 символов):")
            print(response.text[:300])
    elif response.status_code == 401:
        print("ОШИБКА 401 Unauthorized")
        print("Неверный API ключ")
        print()
        print("Проверьте:")
        print("1. Правильность ключа в файле .env")
        print("2. Что ключ не содержит лишних пробелов")
        print("3. Что ключ активен на сайте openrouter.ai")
    elif response.status_code == 429:
        print("ОШИБКА 429 Too Many Requests")
        print("Превышен лимит запросов")
        print("Попробуйте позже или увеличьте лимит в настройках аккаунта")
    else:
        print("ОШИБКА", response.status_code)
        print("Ответ сервера (первые 500 символов):")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("ОШИБКА: Таймаут при запросе")
    print("Проверьте интернет-соединение")
except requests.exceptions.RequestException as e:
    print("ОШИБКА сети:", str(e))
except Exception as e:
    print("НЕОЖИДАННАЯ ОШИБКА:", str(e))

print()
print("=" * 60)
input("Нажмите Enter для выхода...")



