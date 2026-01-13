"""Добавление моделей, доступных на территории РФ"""
import db

# Инициализация БД
db.init_db()

# Модели, которые обычно доступны в РФ через OpenRouter
# Эти модели от китайских и международных провайдеров, обычно не блокируются
russia_models = [
    {
        "name": "DeepSeek Chat",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "deepseek/deepseek-chat",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "DeepSeek Coder",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "deepseek/deepseek-coder",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "Qwen 2.5 72B",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "qwen/qwen-2.5-72b-instruct",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "Qwen 2.5 32B",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "qwen/qwen-2.5-32b-instruct",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    }
]

print("=" * 80)
print("Добавление моделей, доступных на территории РФ")
print("=" * 80)
print()
print("Добавляемые модели:")
print("1. DeepSeek Chat - китайская модель, обычно доступна в РФ")
print("2. DeepSeek Coder - китайская модель для программирования")
print("3. Qwen 2.5 72B - китайская модель от Alibaba")
print("4. Qwen 2.5 32B - более легкая версия Qwen")
print()
print("Эти модели обычно работают без ограничений в РФ")
print("=" * 80)
print()

added_count = 0
for model in russia_models:
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
            print(f"  API ID: {model['api_id']}")
            added_count += 1
        else:
            print(f"- Модель уже существует: {model['name']}")
    except Exception as e:
        print(f"✗ Ошибка при добавлении {model['name']}: {e}")

print()
print("=" * 80)
print(f"Добавлено новых моделей: {added_count}")
print("=" * 80)
print()
print("Примечание:")
print("- Эти модели доступны через OpenRouter")
print("- Обычно работают без ограничений на территории РФ")
print("- Используют ваш OPENROUTER_API_KEY из файла .env")
print()
print("Готово! Модели добавлены и активированы.")

