import db

db.init_db()
models = db.get_models()

print("Все модели в базе данных:")
print("-" * 80)
for m in models:
    print(f"ID: {m['id']}")
    print(f"  Название: {m['name']}")
    print(f"  Тип API: {m['model_type']}")
    print(f"  URL: {m['api_url']}")
    print(f"  API ID: {m['api_id']}")
    print(f"  Активна: {'Да' if m['is_active'] == 1 else 'Нет'}")
    print()

