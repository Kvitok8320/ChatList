"""Скрипт для проверки настроек моделей"""
import db
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Проверка базы данных ===")
db.init_db()
models = db.get_active_models()
print(f"Активных моделей: {len(models)}")

if len(models) == 0:
    print("\n❌ НЕТ АКТИВНЫХ МОДЕЛЕЙ!")
    print("Добавьте модели через меню 'Управление' -> 'Модели...'")
else:
    print("\nАктивные модели:")
    for m in models:
        print(f"  - {m['name']} ({m['model_type']})")
        api_key_env = m.get('api_key_env', '')
        api_key = os.getenv(api_key_env)
        if api_key:
            print(f"    ✓ API ключ найден: {api_key_env}")
        else:
            print(f"    ✗ API ключ НЕ найден: {api_key_env}")
            print(f"    Проверьте файл .env")

print("\n=== Проверка переменных окружения ===")
env_vars = ['OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'GROQ_API_KEY', 'OPENROUTER_API_KEY']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"  ✓ {var}: {'*' * min(10, len(value))}")
    else:
        print(f"  ✗ {var}: не установлен")




