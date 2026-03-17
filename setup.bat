@echo off
chcp 65001 >nul
echo =========================================
echo   ВСТАНОВЛЕННЯ СИСТЕМИ UNIQ-LOW
echo =========================================

:: 1. Перевірка Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ПОМИЛКА] Python не знайдено на цьому комп'ютері!
    echo Будь ласка, скачайте його з сайту: https://www.python.org/downloads/
    echo ВАЖЛИВО: Під час встановлення ОБОВ'ЯЗКОВО поставте галочку "Add Python to PATH" внизу вікна!
    echo Після встановлення Python запустіть цей файл ще раз.
    pause
    exit
)
echo [ОК] Python знайдено.

:: 2. Перевірка Git
git --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ПОМИЛКА] Git не знайдено! Починаю автоматичне встановлення Git...
    winget install --id Git.Git -e --source winget
    echo Перезапустіть цей файл після того, як Git встановиться.
    pause
    exit
)
echo [ОК] Git знайдено.

:: 3. Налаштування Git (щоб не було помилок при відправці)
echo Налаштовую Git...
git config --global user.name "UniqLowAdmin"
git config --global user.email "admin@uniqlow.com"

:: 4. Встановлення бібліотек Python
echo Встановлюю необхідні модулі (це може зайняти хвилину)...
pip install python-telegram-bot selenium webdriver-manager >nul

:: 5. Запуск Менеджера
echo =========================================
echo ВСЕ ГОТОВО! Запускаю систему...
echo =========================================
python manager.py
pause