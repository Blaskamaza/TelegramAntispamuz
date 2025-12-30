@echo off
chcp 65001 >nul
color 0A

echo ================================
echo   SAMURAI BOT AUTO SETUP
echo ================================
echo.

REM Проверка что мы в правильной папке
if not exist "bot.py" (
    color 0C
    echo ОШИБКА: Запусти этот скрипт в папке samurai-main!
    echo Пример: cd C:\Users\user\Desktop\samurai-main
    echo Затем: setup_samurai.bat
    pause
    exit /b
)

echo [1/7] Создание .env файла...

REM Создать .env
(
echo # Samurai Bot Configuration
echo.
echo # Bot token from @BotFather
echo BOT_TOKEN=8289581557:AAH5uw-f10jnUAUhFea509osIfYBSuJNlBg
echo.
echo # Your Telegram User ID
echo BOT_OWNER=6832861588
echo.
echo # Main group chat ID
echo GROUPS_MAIN=0
echo.
echo # Reports group chat ID
echo GROUPS_REPORTS=0
echo.
echo # Logs group chat ID
echo GROUPS_LOGS=0
echo.
echo # Linked channel ID
echo LINKED_CHANNEL=
echo.
echo # Database URL
echo DB_URL=sqlite:///samurai.db
echo.
echo # Gemini API Key
echo GEMINI_API_KEY=AIzaSyDIEemIIhvsoGYZkLqOLSggKho0w49h9U4
) > .env

echo   ✓ .env создан
echo.

REM ========================================
echo [2/7] Создание виртуального окружения...

if exist "venv" (
    echo   ⚠ venv уже существует, пропускаю...
) else (
    python -m venv venv
    echo   ✓ venv создан
)
echo.

REM ========================================
echo [3/7] Установка зависимостей...
echo   (это займёт 5-10 минут)

call venv\Scripts\activate.bat
pip install -q -r requirements.txt
pip install -q google-generativeai

echo   ✓ Зависимости установлены
echo.

REM ========================================
echo [4/7] Подготовка db_init.py...

REM Комментируем exit строку в db_init.py
powershell -Command "(Get-Content db_init.py) -replace 'exit\(\"COMMENT THIS LINE', '#exit(\"COMMENT THIS LINE' | Set-Content db_init.py"

echo   ✓ db_init.py готов
echo.

REM ========================================
echo [5/7] Инициализация базы данных...

python db_init.py

if exist "samurai.db" (
    echo   ✓ База данных создана
) else (
    echo   ⚠ Проверьте вывод выше
)
echo.

REM ========================================
echo [6/7] Добавление узбекского языка...

REM Создать папку
if not exist "locales\uz" mkdir locales\uz

REM Копировать файлы если они есть
if exist "uzbek_strings.ftl" (
    copy /Y uzbek_strings.ftl locales\uz\strings.ftl >nul
    echo   ✓ strings.ftl скопирован
) else (
    echo   ⚠ uzbek_strings.ftl не найден - скачай и перезапусти
)

if exist "uzbek_announcements.ftl" (
    copy /Y uzbek_announcements.ftl locales\uz\announcements.ftl >nul
    echo   ✓ announcements.ftl скопирован
) else (
    echo   ⚠ uzbek_announcements.ftl не найден - скачай и перезапусти
)

REM Обновить i18n.py
echo   Обновление i18n.py...
powershell -Command "(Get-Content core\i18n.py) -replace 'LOCALES = \[\"en\", \"ru\"\]', 'LOCALES = [\"en\", \"ru\", \"uz\"]' | Set-Content core\i18n.py"

REM Обновить config.toml
echo   Обновление config.toml...
powershell -Command "$c = Get-Content config.toml; $c = $c -replace 'default = \"ru\"', 'default = \"uz\"'; $c = $c -replace 'available = \[\"ru\", \"en\"\]', 'available = [\"ru\", \"en\", \"uz\"]'; Set-Content config.toml $c"

echo   ✓ Узбекский язык добавлен
echo.

REM ========================================
echo [7/7] Проверка...

set ALL_GOOD=1

if not exist ".env" (
    echo   ✗ .env не создан
    set ALL_GOOD=0
)

if not exist "venv" (
    echo   ✗ venv не создан
    set ALL_GOOD=0
)

if not exist "samurai.db" (
    echo   ✗ База данных не создана
    set ALL_GOOD=0
)

if not exist "locales\uz\strings.ftl" (
    echo   ⚠ Узбекские файлы не скопированы
    echo      Скачай uzbek_strings.ftl и uzbek_announcements.ftl
    echo      Помести в папку samurai-main и перезапусти
)

echo.

REM ========================================
echo ================================
if %ALL_GOOD%==1 (
    color 0A
    echo   ✓ УСТАНОВКА ЗАВЕРШЕНА!
) else (
    color 0E
    echo   ⚠ УСТАНОВКА ЗАВЕРШЕНА С ПРЕДУПРЕЖДЕНИЯМИ
)
echo ================================
echo.

color 0B
echo ЧТО ДЕЛАТЬ ДАЛЬШЕ:
echo.
echo 1. Запусти бота:
echo    python bot.py
echo.
echo 2. Открой Telegram и найди своего бота
echo.
echo 3. Попробуй команды:
echo    !ping
echo    !me
echo    !help
echo.

set /p RUN="Хочешь запустить бота прямо сейчас? (y/n): "

if /i "%RUN%"=="y" (
    echo.
    echo Запускаю бота...
    echo Для остановки нажми Ctrl+C
    echo.
    python bot.py
)

pause
