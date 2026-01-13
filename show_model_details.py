import db

db.init_db()
models = db.get_models()

print("=" * 80)
print("Детали всех моделей в базе данных:")
print("=" * 80)
print()

for m in models:
    print(f"ID: {m['id']}")
    print(f"  Название: {m['name']}")
    print(f"  API URL: {m['api_url']}")
    print(f"  API ID модели: {m['api_id']}")
    print(f"  Переменная API-ключа: {m['api_key_env']}")
    print(f"  Тип API: {m['model_type']}")
    print(f"  Активна: {'Да' if m['is_active'] == 1 else 'Нет'}")
    print()

print("=" * 80)
print("Важно:")
print("=" * 80)
print("1. API URL хранится в БАЗЕ ДАННЫХ (таблица models, поле api_url)")
print("2. API КЛЮЧ хранится в ФАЙЛЕ .env (переменная OPENROUTER_API_KEY)")
print("3. URL и ключ - это разные вещи:")
print("   - URL указывает, КУДА отправлять запрос")
print("   - Ключ используется для АУТЕНТИФИКАЦИИ")
print()
print("Для OpenRouter все модели должны иметь:")
print("  API URL: https://openrouter.ai/api/v1/chat/completions")
print("  Переменная API-ключа: OPENROUTER_API_KEY")
print()

