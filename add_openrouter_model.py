"""Скрипт для быстрого добавления модели OpenRouter"""
import db

# Инициализация БД
db.init_db()

# Добавляем популярные модели OpenRouter
models_to_add = [
    {
        "name": "GPT-4 (OpenRouter)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "openai/gpt-4",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "Claude 3 Opus (OpenRouter)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "anthropic/claude-3-opus",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "Claude 3 Sonnet (OpenRouter)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "anthropic/claude-3-sonnet",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "GPT-3.5 Turbo (OpenRouter)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "openai/gpt-3.5-turbo",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    }
]

print("Добавление моделей OpenRouter...")
for model in models_to_add:
    try:
        # Проверяем, не существует ли уже такая модель
        existing_models = db.get_models()
        exists = any(m.get("name") == model["name"] for m in existing_models)
        
        if not exists:
            model_id = db.add_model(
                name=model["name"],
                api_url=model["api_url"],
                api_id=model["api_id"],
                api_key_env=model["api_key_env"],
                model_type=model["model_type"],
                is_active=model["is_active"]
            )
            print(f"✓ Добавлена модель: {model['name']} (ID: {model_id})")
        else:
            print(f"- Модель уже существует: {model['name']}")
    except Exception as e:
        print(f"✗ Ошибка при добавлении {model['name']}: {e}")

print("\nГотово! Теперь можно использовать приложение.")


