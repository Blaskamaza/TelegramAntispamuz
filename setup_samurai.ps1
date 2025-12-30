# ========================================
# SAMURAI BOT - АВТОМАТИЧЕСКАЯ УСТАНОВКА
# ========================================
# Этот скрипт автоматически настроит твой Samurai антиспам бот
# Запусти его в PowerShell от имени администратора

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  SAMURAI BOT AUTO SETUP" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Проверка что мы в правильной папке
if (-not (Test-Path "bot.py")) {
    Write-Host "ОШИБКА: Запусти этот скрипт в папке samurai-main!" -ForegroundColor Red
    Write-Host "Пример: cd C:\Users\user\Desktop\samurai-main" -ForegroundColor Yellow
    Write-Host "Затем: .\setup_samurai.ps1" -ForegroundColor Yellow
    exit
}

Write-Host "[1/7] Создание .env файла..." -ForegroundColor Green

# Создать .env
$envContent = @"
# Samurai Bot Configuration

# Bot token from @BotFather
BOT_TOKEN=8289581557:AAH5uw-f10jnUAUhFea509osIfYBSuJNlBg

# Your Telegram User ID
BOT_OWNER=6832861588

# Main group chat ID (configure later)
GROUPS_MAIN=0

# Reports group chat ID (configure later)
GROUPS_REPORTS=0

# Logs group chat ID (configure later)
GROUPS_LOGS=0

# Linked channel ID (optional)
LINKED_CHANNEL=

# Database URL
DB_URL=sqlite:///samurai.db

# Gemini API Key
GEMINI_API_KEY=AIzaSyDIEemIIhvsoGYZkLqOLSggKho0w49h9U4
"@

Set-Content -Path ".env" -Value $envContent -Encoding UTF8
Write-Host "  ✅ .env создан" -ForegroundColor Green

# ========================================
Write-Host ""
Write-Host "[2/7] Создание виртуального окружения..." -ForegroundColor Green

if (Test-Path "venv") {
    Write-Host "  ⚠️  venv уже существует, пропускаю..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "  ✅ venv создан" -ForegroundColor Green
}

# ========================================
Write-Host ""
Write-Host "[3/7] Установка зависимостей..." -ForegroundColor Green
Write-Host "  (это займёт 5-10 минут)" -ForegroundColor Yellow

.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
pip install -q google-generativeai

Write-Host "  ✅ Зависимости установлены" -ForegroundColor Green

# ========================================
Write-Host ""
Write-Host "[4/7] Подготовка db_init.py..." -ForegroundColor Green

# Читаем файл
$dbInitContent = Get-Content "db_init.py" -Raw

# Комментируем exit строку
$dbInitContent = $dbInitContent -replace 'exit\("COMMENT THIS LINE', '#exit("COMMENT THIS LINE'

# Сохраняем
Set-Content -Path "db_init.py" -Value $dbInitContent -Encoding UTF8
Write-Host "  ✅ db_init.py готов" -ForegroundColor Green

# ========================================
Write-Host ""
Write-Host "[5/7] Инициализация базы данных..." -ForegroundColor Green

python db_init.py

if (Test-Path "samurai.db") {
    Write-Host "  ✅ База данных создана" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Проверьте вывод выше" -ForegroundColor Yellow
}

# ========================================
Write-Host ""
Write-Host "[6/7] Добавление узбекского языка..." -ForegroundColor Green

# Создать папку
New-Item -ItemType Directory -Force -Path "locales\uz" | Out-Null

# Проверить что файлы скачаны
if (Test-Path "uzbek_strings.ftl") {
    Copy-Item "uzbek_strings.ftl" "locales\uz\strings.ftl"
    Write-Host "  ✅ strings.ftl скопирован" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  uzbek_strings.ftl не найден - скачай его и перезапусти" -ForegroundColor Yellow
}

if (Test-Path "uzbek_announcements.ftl") {
    Copy-Item "uzbek_announcements.ftl" "locales\uz\announcements.ftl"
    Write-Host "  ✅ announcements.ftl скопирован" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  uzbek_announcements.ftl не найден - скачай его и перезапусти" -ForegroundColor Yellow
}

# Обновить i18n.py
Write-Host "  Обновление i18n.py..." -ForegroundColor Cyan
$i18nContent = Get-Content "core\i18n.py" -Raw
$i18nContent = $i18nContent -replace 'LOCALES = \["en", "ru"\]', 'LOCALES = ["en", "ru", "uz"]'
Set-Content -Path "core\i18n.py" -Value $i18nContent -Encoding UTF8

# Обновить config.toml
Write-Host "  Обновление config.toml..." -ForegroundColor Cyan
$configContent = Get-Content "config.toml" -Raw
$configContent = $configContent -replace 'default = "ru"', 'default = "uz"'
$configContent = $configContent -replace 'available = \["ru", "en"\]', 'available = ["ru", "en", "uz"]'
Set-Content -Path "config.toml" -Value $configContent -Encoding UTF8

Write-Host "  ✅ Узбекский язык добавлен" -ForegroundColor Green

# ========================================
Write-Host ""
Write-Host "[7/7] Проверка..." -ForegroundColor Green

$allGood = $true

if (-not (Test-Path ".env")) {
    Write-Host "  ❌ .env не создан" -ForegroundColor Red
    $allGood = $false
}

if (-not (Test-Path "venv")) {
    Write-Host "  ❌ venv не создан" -ForegroundColor Red
    $allGood = $false
}

if (-not (Test-Path "samurai.db")) {
    Write-Host "  ❌ База данных не создана" -ForegroundColor Red
    $allGood = $false
}

if (-not (Test-Path "locales\uz\strings.ftl")) {
    Write-Host "  ⚠️  Узбекские файлы не скопированы" -ForegroundColor Yellow
    Write-Host "     Скачай uzbek_strings.ftl и uzbek_announcements.ftl" -ForegroundColor Yellow
    Write-Host "     Помести в папку samurai-main и перезапусти скрипт" -ForegroundColor Yellow
}

# ========================================
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  ✅ УСТАНОВКА ЗАВЕРШЕНА!" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  УСТАНОВКА ЗАВЕРШЕНА С ПРЕДУПРЕЖДЕНИЯМИ" -ForegroundColor Yellow
}
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "ЧТО ДЕЛАТЬ ДАЛЬШЕ:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Запусти бота:" -ForegroundColor White
Write-Host "   python bot.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Открой Telegram и найди своего бота" -ForegroundColor White
Write-Host ""
Write-Host "3. Попробуй команды:" -ForegroundColor White
Write-Host "   !ping" -ForegroundColor Yellow
Write-Host "   !me" -ForegroundColor Yellow
Write-Host "   !help" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Создай группу и добавь бота туда" -ForegroundColor White
Write-Host ""
Write-Host "ПОДДЕРЖКА:" -ForegroundColor Cyan
Write-Host "  Если что-то не работает - скажи мне!" -ForegroundColor White
Write-Host ""

# Предложить запустить бота
Write-Host "Хочешь запустить бота прямо сейчас? (y/n): " -ForegroundColor Green -NoNewline
$response = Read-Host

if ($response -eq "y" -or $response -eq "Y") {
    Write-Host ""
    Write-Host "Запускаю бота..." -ForegroundColor Green
    Write-Host "Для остановки нажми Ctrl+C" -ForegroundColor Yellow
    Write-Host ""
    python bot.py
}
