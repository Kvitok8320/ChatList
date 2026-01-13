"""Тестовый скрипт для проверки OpenRouter API"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ OPENROUTER_API_KEY не найден в .env файле")
    exit(1)

print(f"✓ API ключ найден: {api_key[:10]}...{api_key[-4:]}")
print(f"  Длина ключа: {len(api_key)} символов")
print()

# Тестируем простой запрос
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

print("Отправка тестового запроса к OpenRouter API...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Статус код: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if "choices" in result:
            message = result["choices"][0]["message"]["content"]
            print(f"✓ Успешно! Ответ: {message}")
        else:
            print(f"❌ Неожиданный формат ответа: {result}")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Проблема с API ключом или правами доступа")
        print(f"   Ответ сервера: {response.text[:500]}")
    elif response.status_code == 401:
        print("❌ 401 Unauthorized - Неверный API ключ")
        print(f"   Ответ сервера: {response.text[:500]}")
    else:
        print(f"❌ Ошибка {response.status_code}")
        print(f"   Ответ: {response.text[:500]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Ошибка сети: {e}")

