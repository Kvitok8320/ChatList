@echo off
REM Скрипт для создания установщика ChatList
echo ========================================
echo Создание установщика ChatList
echo ========================================
echo.

REM Проверяем наличие Inno Setup Compiler
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
)

if "%ISCC_PATH%"=="" (
    echo [ОШИБКА] Inno Setup Compiler не найден!
    echo.
    echo Пожалуйста, установите Inno Setup:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo После установки запустите этот скрипт снова.
    echo.
    pause
    exit /b 1
)

echo Найден Inno Setup Compiler: %ISCC_PATH%
echo.

REM Проверяем наличие необходимых файлов
if not exist "ChatList.iss" (
    echo [ОШИБКА] Файл ChatList.iss не найден!
    echo Запустите: python create_installer.py
    pause
    exit /b 1
)

if not exist "dist\ChatListApp-1.0.0.exe" (
    echo [ОШИБКА] Исполняемый файл dist\ChatListApp-1.0.0.exe не найден!
    echo Сначала соберите исполняемый файл: python -m PyInstaller ChatListApp.spec
    pause
    exit /b 1
)

if not exist "app.ico" (
    echo [ОШИБКА] Файл app.ico не найден!
    pause
    exit /b 1
)

echo Все необходимые файлы найдены.
echo.
echo Запуск компиляции установщика...
echo.

REM Создаем папку installer, если её нет
if not exist "installer" mkdir installer

REM Компилируем установщик
"%ISCC_PATH%" "ChatList.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Установщик успешно создан!
    echo ========================================
    echo.
    echo Файл установщика: installer\ChatList-Setup-1.0.0.exe
    echo.
) else (
    echo.
    echo ========================================
    echo Ошибка при создании установщика!
    echo ========================================
    echo.
)

pause

