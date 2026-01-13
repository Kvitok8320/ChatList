# Схема базы данных ChatList

## Общая информация

База данных: SQLite  
Файл базы данных: `chatlist.db` (создается автоматически при первом запуске)

## Таблицы

### 1. Таблица `prompts` (Промты)

Хранит сохраненные промты пользователя.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| date | TEXT | Дата создания промта | NOT NULL, формат: ISO 8601 (YYYY-MM-DD HH:MM:SS) |
| prompt | TEXT | Текст промта | NOT NULL |
| tags | TEXT | Теги через запятую | Может быть NULL |

**Индексы:**
- `idx_prompts_date` на поле `date`
- `idx_prompts_tags` на поле `tags`

**Пример запроса создания:**
```sql
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    prompt TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX idx_prompts_date ON prompts(date);
CREATE INDEX idx_prompts_tags ON prompts(tags);
```

---

### 2. Таблица `models` (Модели нейросетей)

Хранит информацию о доступных моделях нейросетей.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | Название модели | NOT NULL, UNIQUE |
| api_url | TEXT | URL API для запросов | NOT NULL |
| api_id | TEXT | Идентификатор модели в API | NOT NULL |
| api_key_env | TEXT | Имя переменной окружения для API-ключа | NOT NULL |
| is_active | INTEGER | Активна ли модель (1 - да, 0 - нет) | NOT NULL, DEFAULT 1 |
| model_type | TEXT | Тип модели (openai, deepseek, groq и т.д.) | NOT NULL |

**Индексы:**
- `idx_models_name` на поле `name`
- `idx_models_is_active` на поле `is_active`

**Пример запроса создания:**
```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    api_url TEXT NOT NULL,
    api_id TEXT NOT NULL,
    api_key_env TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    model_type TEXT NOT NULL
);

CREATE INDEX idx_models_name ON models(name);
CREATE INDEX idx_models_is_active ON models(is_active);
```

**Примечание:** API-ключи хранятся в файле `.env` в виде переменных окружения. Поле `api_key_env` содержит имя переменной (например, "OPENAI_API_KEY").

---

### 3. Таблица `results` (Результаты)

Хранит сохраненные результаты сравнения моделей.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| prompt_id | INTEGER | Ссылка на промт | FOREIGN KEY REFERENCES prompts(id) |
| model_id | INTEGER | Ссылка на модель | FOREIGN KEY REFERENCES models(id) |
| response | TEXT | Ответ модели | NOT NULL |
| date | TEXT | Дата сохранения результата | NOT NULL, формат: ISO 8601 |
| prompt_text | TEXT | Текст промта на момент сохранения | NOT NULL (для истории) |

**Индексы:**
- `idx_results_prompt_id` на поле `prompt_id`
- `idx_results_model_id` на поле `model_id`
- `idx_results_date` на поле `date`

**Пример запроса создания:**
```sql
CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER,
    model_id INTEGER,
    response TEXT NOT NULL,
    date TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);

CREATE INDEX idx_results_prompt_id ON results(prompt_id);
CREATE INDEX idx_results_model_id ON results(model_id);
CREATE INDEX idx_results_date ON results(date);
```

**Примечание:** Поле `prompt_text` сохраняется для того, чтобы можно было видеть историю даже если промт был удален или изменен.

---

### 4. Таблица `settings` (Настройки)

Хранит настройки программы в формате ключ-значение.

| Поле | Тип | Описание | Ограничения |
|------|-----|----------|-------------|
| id | INTEGER | Первичный ключ | PRIMARY KEY AUTOINCREMENT |
| key | TEXT | Ключ настройки | NOT NULL, UNIQUE |
| value | TEXT | Значение настройки | Может быть NULL |

**Индексы:**
- `idx_settings_key` на поле `key` (уникальный индекс)

**Пример запроса создания:**
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT
);

CREATE UNIQUE INDEX idx_settings_key ON settings(key);
```

**Примеры настроек:**
- `timeout` - таймаут для HTTP-запросов (по умолчанию: "30")
- `log_level` - уровень логирования (по умолчанию: "INFO")
- `default_export_format` - формат экспорта по умолчанию (по умолчанию: "markdown")

---

## Связи между таблицами

```
prompts (1) ──< (N) results
models (1) ──< (N) results
```

- Один промт может иметь множество результатов
- Одна модель может иметь множество результатов
- Результат связан с одним промтом и одной моделью

---

## Примеры данных

### Таблица `models`:
```sql
INSERT INTO models (name, api_url, api_id, api_key_env, is_active, model_type) VALUES
('GPT-4', 'https://api.openai.com/v1/chat/completions', 'gpt-4', 'OPENAI_API_KEY', 1, 'openai'),
('DeepSeek Chat', 'https://api.deepseek.com/v1/chat/completions', 'deepseek-chat', 'DEEPSEEK_API_KEY', 1, 'deepseek'),
('Llama 3 (Groq)', 'https://api.groq.com/openai/v1/chat/completions', 'llama-3-70b-8192', 'GROQ_API_KEY', 1, 'groq');
```

### Таблица `prompts`:
```sql
INSERT INTO prompts (date, prompt, tags) VALUES
('2024-01-15 10:30:00', 'Объясни квантовую физику простыми словами', 'наука, физика'),
('2024-01-15 11:00:00', 'Напиши код на Python для работы с API', 'программирование, python');
```

### Таблица `results`:
```sql
INSERT INTO results (prompt_id, model_id, response, date, prompt_text) VALUES
(1, 1, 'Квантовая физика изучает...', '2024-01-15 10:35:00', 'Объясни квантовую физику простыми словами'),
(1, 2, 'Квантовая механика - это раздел...', '2024-01-15 10:35:05', 'Объясни квантовую физику простыми словами');
```

---

## Миграции и версионирование

При необходимости можно добавить таблицу `schema_version` для отслеживания версии схемы БД:

```sql
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_date TEXT NOT NULL
);
```

