"""Проверка URL для всех моделей"""
import db

db.init_db()
models = db.get_models()

correct_url = "https://openrouter.ai/api/v1/chat/completions"

print("=" * 80)
print("Проверка URL для всех моделей")
print("=" * 80)
print()
print(f"Правильный URL: {correct_url}")
print()
print("Статус моделей:")
print("-" * 80)

all_correct = True
for model in models:
    if model["api_url"] == correct_url:
        status = "✓"
    else:
        status = "✗"
        all_correct = False
    
    print(f"{status} {model['name']}")
    if model["api_url"] != correct_url:
        print(f"    Текущий URL: {model['api_url']}")
        print(f"    Должен быть: {correct_url}")

print()
print("=" * 80)
if all_correct:
    print("✓ Все модели используют правильный URL!")
else:
    print("✗ Некоторые модели имеют неправильный URL")
    print("  Запустите fix_urls.py для исправления")
print("=" * 80)

