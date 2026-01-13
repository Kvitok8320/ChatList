"""Удаление неработающих моделей и добавление бесплатных"""
import db

db.init_db()

# Получаем все модели
all_models = db.get_models()

print("=" * 80)
print("Очистка неработающих моделей")
print("=" * 80)
print()

# Список моделей, которые обычно не работают или дают ошибки
# (можно расширить на основе ваших наблюдений)
problematic_models = [
    "Qwen: Qwen3 Coder 480B A35B",  # Эта модель давала ошибки
    "DeepSeek: R1 0528",  # Возможно, тоже проблемная
]

deleted_count = 0
for model in all_models:
    if model["name"] in problematic_models:
        try:
            db.delete_model(model["id"])
            print(f"✓ Удалена модель: {model['name']} (ID: {model['id']})")
            deleted_count += 1
        except Exception as e:
            print(f"✗ Ошибка при удалении {model['name']}: {e}")

print()
print(f"Удалено моделей: {deleted_count}")
print()

# Бесплатные модели, которые обычно работают стабильно
# На OpenRouter есть бесплатные модели, но нужно проверить актуальный список
free_models = [
    {
        "name": "Meta Llama 3.1 8B (Free)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "meta-llama/llama-3.1-8b-instruct:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "Mistral 7B (Free)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "mistralai/mistral-7b-instruct:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    },
    {
        "name": "Google Gemma 7B (Free)",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_id": "google/gemma-7b-it:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_type": "openrouter",
        "is_active": 1
    }
]

print("=" * 80)
print("Добавление бесплатных моделей")
print("=" * 80)
print()
print("Добавляемые бесплатные модели:")
print("1. Meta Llama 3.1 8B - бесплатная модель от Meta")
print("2. Mistral 7B - бесплатная модель от Mistral AI")
print("3. Google Gemma 7B - бесплатная модель от Google")
print()
print("=" * 80)
print()

added_count = 0
for model in free_models:
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
print(f"Итого: удалено {deleted_count}, добавлено {added_count}")
print("=" * 80)

