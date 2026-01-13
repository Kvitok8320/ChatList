# Как проверить работу API ключа OpenRouter

## Способ 1: Через скрипт проверки

Запустите один из скриптов:

```bash
python check_key.py
```

или

```bash
python verify_key.py
```

Скрипт покажет:
- Найден ли ключ в файле .env
- Правильный ли формат ключа
- Работает ли ключ (отправит тестовый запрос)

## Способ 2: Через приложение ChatList

1. Запустите приложение: `python main.py`
2. Введите простой промт, например: "Привет"
3. Нажмите "Отправить запрос"
4. Если модели отвечают - ключ работает
5. Если видите ошибки 403/401 - ключ неверный

## Способ 3: Через curl (командная строка)

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY_HERE" \
  -H "HTTP-Referer: https://github.com/chatlist" \
  -H "X-Title: ChatList" \
  -d '{
    "model": "openai/gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

Замените `YOUR_API_KEY_HERE` на ваш реальный ключ.

## Способ 4: Через Python интерактивно

Откройте Python и выполните:

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
print(f"Key: {api_key[:20]}...")

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/chatlist",
        "X-Title": "ChatList"
    },
    json={
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hi"}]
    }
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS! Key works!")
    print(response.json()["choices"][0]["message"]["content"])
else:
    print("ERROR:", response.text[:200])
```

## Что проверить, если ключ не работает:

1. **Формат ключа**: Должен начинаться с `sk-or-v1-`
2. **Файл .env**: 
   - Должен быть в корне проекта
   - Строка: `OPENROUTER_API_KEY=sk-or-v1-...` (без кавычек)
   - Нет лишних пробелов
3. **Активность ключа**: Проверьте на https://openrouter.ai/keys
4. **Баланс**: Убедитесь, что есть средства на счету (если требуется)

## Интерпретация результатов:

- **200 OK** - ключ работает! ✅
- **401 Unauthorized** - неверный ключ ❌
- **403 Forbidden** - ключ верный, но нет доступа к модели или недостаточно прав ❌
- **429 Too Many Requests** - превышен лимит запросов ⚠️

