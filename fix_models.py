"""Скрипт для исправления настроек моделей"""
import db

db.init_db()

# Получаем все модели
all_models = db.get_models()

print("Проверка и исправление настроек моделей...\n")

fixed_count = 0
for model in all_models:
    model_id = model["id"]
    name = model["name"]
    api_url = model["api_url"]
    model_type = model["model_type"]
    
    # Определяем правильный тип по URL
    correct_type = None
    if "openrouter.ai" in api_url.lower():
        correct_type = "openrouter"
    elif "deepseek.com" in api_url.lower():
        correct_type = "deepseek"
    elif "groq.com" in api_url.lower():
        correct_type = "groq"
    elif "openai.com" in api_url.lower():
        correct_type = "openai"
    
    # Если тип неправильный, исправляем
    if correct_type and model_type.lower() != correct_type:
        print(f"Исправление модели: {name}")
        print(f"  Старый тип: {model_type}")
        print(f"  Новый тип: {correct_type}")
        
        try:
            db.update_model(
                model_id=model_id,
                name=model["name"],
                api_url=model["api_url"],
                api_id=model["api_id"],
                api_key_env=model["api_key_env"],
                model_type=correct_type,
                is_active=model["is_active"]
            )
            print(f"  ✓ Исправлено\n")
            fixed_count += 1
        except Exception as e:
            print(f"  ✗ Ошибка: {e}\n")
    else:
        print(f"✓ {name}: тип правильный ({model_type})")

print(f"\nИсправлено моделей: {fixed_count}")



