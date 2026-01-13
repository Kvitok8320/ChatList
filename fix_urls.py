"""Исправление URL для моделей OpenRouter"""
import db

db.init_db()
models = db.get_models()

correct_url = "https://openrouter.ai/api/v1/chat/completions"

print("Исправление URL для моделей OpenRouter...")
print()

fixed_count = 0
for model in models:
    if model["api_url"] != correct_url and "openrouter" in model["api_url"].lower():
        print(f"Модель: {model['name']}")
        print(f"  Старый URL: {model['api_url']}")
        print(f"  Новый URL: {correct_url}")
        
        try:
            db.update_model(
                model_id=model["id"],
                name=model["name"],
                api_url=correct_url,
                api_id=model["api_id"],
                api_key_env=model["api_key_env"],
                model_type=model["model_type"],
                is_active=model["is_active"]
            )
            print(f"  ✓ Исправлено")
            fixed_count += 1
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
        print()

print(f"Исправлено моделей: {fixed_count}")

