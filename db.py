"""
Модуль для работы с базой данных SQLite
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


DB_NAME = "chatlist.db"


def get_connection():
    """Создает и возвращает соединение с базой данных"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Создание таблицы prompts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            prompt TEXT NOT NULL,
            tags TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_date ON prompts(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prompts_tags ON prompts(tags)")
    
    # Создание таблицы models
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            api_url TEXT NOT NULL,
            api_id TEXT NOT NULL,
            api_key_env TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            model_type TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_name ON models(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_models_is_active ON models(is_active)")
    
    # Создание таблицы results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id INTEGER,
            model_id INTEGER,
            response TEXT NOT NULL,
            date TEXT NOT NULL,
            prompt_text TEXT NOT NULL,
            FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE SET NULL,
            FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_prompt_id ON results(prompt_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_model_id ON results(model_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_results_date ON results(date)")
    
    # Создание таблицы settings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT
        )
    """)
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_settings_key ON settings(key)")
    
    # Установка значений по умолчанию для настроек
    default_settings = [
        ("timeout", "30"),
        ("log_level", "INFO"),
        ("default_export_format", "markdown")
    ]
    for key, value in default_settings:
        cursor.execute("""
            INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))
    
    conn.commit()
    conn.close()


# ========== Функции для работы с таблицей prompts ==========

def add_prompt(prompt: str, tags: Optional[str] = None) -> int:
    """Добавляет новый промт в базу данных"""
    conn = get_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO prompts (date, prompt, tags) VALUES (?, ?, ?)
    """, (date, prompt, tags))
    prompt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prompt_id


def get_prompts(sort_by: str = "date", order: str = "DESC") -> List[Dict]:
    """Получает список всех промтов"""
    valid_sort = {"date", "prompt", "tags"}
    valid_order = {"ASC", "DESC"}
    
    if sort_by not in valid_sort:
        sort_by = "date"
    if order not in valid_order:
        order = "DESC"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, date, prompt, tags FROM prompts 
        ORDER BY {sort_by} {order}
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def search_prompts(query: str, search_in: str = "all") -> List[Dict]:
    """Поиск промтов по тексту"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if search_in == "prompt":
        cursor.execute("""
            SELECT id, date, prompt, tags FROM prompts 
            WHERE prompt LIKE ?
            ORDER BY date DESC
        """, (f"%{query}%",))
    elif search_in == "tags":
        cursor.execute("""
            SELECT id, date, prompt, tags FROM prompts 
            WHERE tags LIKE ?
            ORDER BY date DESC
        """, (f"%{query}%",))
    else:  # all
        cursor.execute("""
            SELECT id, date, prompt, tags FROM prompts 
            WHERE prompt LIKE ? OR tags LIKE ?
            ORDER BY date DESC
        """, (f"%{query}%", f"%{query}%"))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_prompt_by_id(prompt_id: int) -> Optional[Dict]:
    """Получает промт по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, prompt, tags FROM prompts WHERE id = ?", (prompt_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def delete_prompt(prompt_id: int) -> bool:
    """Удаляет промт по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ========== Функции для работы с таблицей models ==========

def add_model(name: str, api_url: str, api_id: str, api_key_env: str, 
              model_type: str, is_active: int = 1) -> int:
    """Добавляет новую модель в базу данных"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO models (name, api_url, api_id, api_key_env, is_active, model_type)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, api_url, api_id, api_key_env, is_active, model_type))
    model_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return model_id


def get_models(sort_by: str = "name", order: str = "ASC") -> List[Dict]:
    """Получает список всех моделей"""
    valid_sort = {"name", "model_type", "is_active"}
    valid_order = {"ASC", "DESC"}
    
    if sort_by not in valid_sort:
        sort_by = "name"
    if order not in valid_order:
        order = "ASC"
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, name, api_url, api_id, api_key_env, is_active, model_type 
        FROM models 
        ORDER BY {sort_by} {order}
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_active_models() -> List[Dict]:
    """Получает список активных моделей"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, api_url, api_id, api_key_env, is_active, model_type 
        FROM models 
        WHERE is_active = 1
        ORDER BY name
    """)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_model_status(model_id: int, is_active: int) -> bool:
    """Обновляет статус активности модели"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE models SET is_active = ? WHERE id = ?", (is_active, model_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def get_model_by_id(model_id: int) -> Optional[Dict]:
    """Получает модель по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, api_url, api_id, api_key_env, is_active, model_type 
        FROM models WHERE id = ?
    """, (model_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def update_model(model_id: int, name: str, api_url: str, api_id: str, 
                 api_key_env: str, model_type: str, is_active: int) -> bool:
    """Обновляет информацию о модели"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE models 
        SET name = ?, api_url = ?, api_id = ?, api_key_env = ?, 
            model_type = ?, is_active = ?
        WHERE id = ?
    """, (name, api_url, api_id, api_key_env, model_type, is_active, model_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def delete_model(model_id: int) -> bool:
    """Удаляет модель по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM models WHERE id = ?", (model_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def search_models(query: str) -> List[Dict]:
    """Поиск моделей по названию или типу"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, api_url, api_id, api_key_env, is_active, model_type 
        FROM models 
        WHERE name LIKE ? OR model_type LIKE ?
        ORDER BY name
    """, (f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ========== Функции для работы с таблицей results ==========

def save_result(prompt_id: Optional[int], model_id: Optional[int], 
                response: str, prompt_text: str) -> int:
    """Сохраняет результат в базу данных"""
    conn = get_connection()
    cursor = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO results (prompt_id, model_id, response, date, prompt_text)
        VALUES (?, ?, ?, ?, ?)
    """, (prompt_id, model_id, response, date, prompt_text))
    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return result_id


def get_results(sort_by: str = "date", order: str = "DESC", 
                limit: Optional[int] = None) -> List[Dict]:
    """Получает список сохраненных результатов"""
    valid_sort = {"date", "prompt_text", "response"}
    valid_order = {"ASC", "DESC"}
    
    if sort_by not in valid_sort:
        sort_by = "date"
    if order not in valid_order:
        order = "DESC"
    
    conn = get_connection()
    cursor = conn.cursor()
    
    query = f"""
        SELECT r.id, r.prompt_id, r.model_id, r.response, r.date, r.prompt_text,
               m.name as model_name, p.prompt as prompt_text_full
        FROM results r
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN prompts p ON r.prompt_id = p.id
        ORDER BY r.{sort_by} {order}
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def search_results(query: str) -> List[Dict]:
    """Поиск результатов по тексту"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, r.prompt_id, r.model_id, r.response, r.date, r.prompt_text,
               m.name as model_name, p.prompt as prompt_text_full
        FROM results r
        LEFT JOIN models m ON r.model_id = m.id
        LEFT JOIN prompts p ON r.prompt_id = p.id
        WHERE r.response LIKE ? OR r.prompt_text LIKE ?
        ORDER BY r.date DESC
    """, (f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def delete_result(result_id: int) -> bool:
    """Удаляет результат по ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# ========== Функции для работы с таблицей settings ==========

def save_setting(key: str, value: str) -> bool:
    """Сохраняет настройку"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
    """, (key, value))
    conn.commit()
    conn.close()
    return True


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Получает значение настройки"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    
    return row["value"] if row else default


def get_all_settings() -> Dict[str, str]:
    """Получает все настройки"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    rows = cursor.fetchall()
    conn.close()
    
    return {row["key"]: row["value"] for row in rows}

