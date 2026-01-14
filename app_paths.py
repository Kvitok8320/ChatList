"""
Модуль для определения путей к файлам приложения
Использует пользовательскую папку для данных, чтобы избежать проблем с правами доступа
"""
import os
import sys
from pathlib import Path


def get_app_data_dir():
    """
    Возвращает путь к папке данных приложения в пользовательской директории
    Для Windows: %LOCALAPPDATA%\ChatList
    Для Linux/Mac: ~/.local/share/ChatList или ~/Library/Application Support/ChatList
    """
    if sys.platform == "win32":
        # Windows: используем LOCALAPPDATA (не синхронизируется с облаком)
        app_data = os.getenv("LOCALAPPDATA", os.path.expanduser("~"))
        app_dir = os.path.join(app_data, "ChatList")
    elif sys.platform == "darwin":
        # macOS
        app_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ChatList")
    else:
        # Linux и другие
        app_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "ChatList")
    
    # Создаем папку, если её нет
    os.makedirs(app_dir, exist_ok=True)
    
    return app_dir


def get_db_path():
    """Возвращает путь к файлу базы данных"""
    return os.path.join(get_app_data_dir(), "chatlist.db")


def get_log_path():
    """Возвращает путь к файлу лога"""
    return os.path.join(get_app_data_dir(), "chatlist.log")


def get_app_dir():
    """
    Возвращает путь к папке установки приложения
    Для разработки - текущая папка, для установленного приложения - папка exe
    """
    if getattr(sys, 'frozen', False):
        # Приложение упаковано (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # Разработка - текущая папка
        return os.path.dirname(os.path.abspath(__file__))

