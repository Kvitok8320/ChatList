# Руководство по публикации ChatList на GitHub

## Подготовка к релизу

### 1. Обновление версии

1. Откройте файл `version.py`
2. Обновите версию (например, с `1.0.0` на `1.0.1`)
3. Сохраните файл

### 2. Сборка исполняемого файла

```bash
# Активируйте виртуальное окружение (если используете)
venv\Scripts\Activate.ps1

# Установите зависимости
pip install -r requirements.txt

# Соберите исполняемый файл
python -m PyInstaller ChatListApp.spec --clean
```

Проверьте, что файл создан: `dist\ChatListApp-{version}.exe`

### 3. Создание установщика

```bash
# Сгенерируйте .iss файл с актуальной версией
python create_installer.py

# Создайте установщик через Inno Setup
# Или используйте скрипт:
.\build_installer.ps1
```

Проверьте, что установщик создан: `installer\ChatList-Setup-{version}.exe`

### 4. Подготовка файлов для релиза

Создайте папку `release` и скопируйте туда:
- `installer\ChatList-Setup-{version}.exe` - установщик
- `README.md` - описание проекта
- `LICENSE` - лицензия (если есть)

## Публикация на GitHub Release

### Шаг 1: Создание тега

```bash
# Убедитесь, что все изменения закоммичены
git add .
git commit -m "Release v{version}"

# Создайте тег
git tag -a v{version} -m "Release version {version}"

# Отправьте тег на GitHub
git push origin v{version}
```

### Шаг 2: Создание Release на GitHub

1. Перейдите на GitHub в ваш репозиторий
2. Нажмите **"Releases"** в правом меню
3. Нажмите **"Draft a new release"**
4. Выберите созданный тег `v{version}`
5. Заголовок: `ChatList v{version}`
6. Скопируйте содержимое из `RELEASE_NOTES_TEMPLATE.md` и заполните
7. Загрузите файл `ChatList-Setup-{version}.exe` в раздел "Attach binaries"
8. Нажмите **"Publish release"**

### Шаг 3: Обновление GitHub Pages (опционально)

Если хотите создать лендинг:

1. Перейдите в **Settings** → **Pages**
2. Выберите источник: **Deploy from a branch**
3. Выберите ветку: **main** (или **gh-pages**)
4. Папка: **/docs** (или **/root**)
5. Скопируйте `index.html` в папку `docs/` (или корень, если выбрали root)
6. Закоммитьте и запушьте изменения

## Структура файлов для релиза

```
ChatList/
├── dist/
│   └── ChatListApp-{version}.exe
├── installer/
│   └── ChatList-Setup-{version}.exe  ← Загрузить на GitHub Release
├── docs/
│   └── index.html  ← Для GitHub Pages
├── version.py
├── RELEASE_GUIDE.md
├── RELEASE_NOTES_TEMPLATE.md
└── ...
```

## Чеклист перед релизом

- [ ] Версия обновлена в `version.py`
- [ ] Исполняемый файл собран и протестирован
- [ ] Установщик создан и протестирован
- [ ] README.md актуален
- [ ] Все изменения закоммичены
- [ ] Тег создан и отправлен на GitHub
- [ ] Release создан на GitHub
- [ ] Установщик загружен в Release
- [ ] Release notes заполнены

## Автоматизация (опционально)

Можно создать GitHub Actions workflow для автоматической сборки и публикации. 
См. `.github/workflows/release.yml` (если создан).

