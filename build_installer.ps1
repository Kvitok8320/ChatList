# Скрипт PowerShell для создания установщика ChatList
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Создание установщика ChatList" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверяем наличие Inno Setup Compiler
$isccPaths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

$isccPath = $null
foreach ($path in $isccPaths) {
    if (Test-Path $path) {
        $isccPath = $path
        break
    }
}

if (-not $isccPath) {
    Write-Host "[ОШИБКА] Inno Setup Compiler не найден!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Пожалуйста, установите Inno Setup:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "После установки запустите этот скрипт снова." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "Найден Inno Setup Compiler: $isccPath" -ForegroundColor Green
Write-Host ""

# Проверяем наличие необходимых файлов
$requiredFiles = @(
    @{Path="ChatList.iss"; Message="Файл ChatList.iss не найден! Запустите: python create_installer.py"},
    @{Path="dist\ChatListApp-1.0.0.exe"; Message="Исполняемый файл не найден! Сначала соберите: python -m PyInstaller ChatListApp.spec"},
    @{Path="app.ico"; Message="Файл app.ico не найден!"}
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file.Path)) {
        Write-Host "[ОШИБКА] $($file.Message)" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "Все необходимые файлы найдены." -ForegroundColor Green
Write-Host ""
Write-Host "Запуск компиляции установщика..." -ForegroundColor Yellow
Write-Host ""

# Создаем папку installer, если её нет
if (-not (Test-Path "installer")) {
    New-Item -ItemType Directory -Path "installer" | Out-Null
}

# Компилируем установщик
$process = Start-Process -FilePath $isccPath -ArgumentList "ChatList.iss" -Wait -NoNewWindow -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Установщик успешно создан!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Файл установщика: installer\ChatList-Setup-1.0.0.exe" -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path "installer\ChatList-Setup-1.0.0.exe") {
        $file = Get-Item "installer\ChatList-Setup-1.0.0.exe"
        $sizeMB = [math]::Round($file.Length / 1MB, 2)
        Write-Host "Размер файла: $sizeMB MB" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Ошибка при создании установщика!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Нажмите Enter для выхода"

