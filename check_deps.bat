@echo off
chcp 65001 >nul
echo === 1. requests 2.31.0 ===
py src/main.py --package requests --repo https://pypi.org --version 2.31.0
echo Код завершения: %ERRORLEVEL%

echo === 2. flask 3.0.0 ===
py src/main.py --package flask --repo https://pypi.org --version 3.0.0
echo Код завершения: %ERRORLEVEL%

echo === 3. Несуществующая версия (404) ===
py src/main.py --package requests --repo https://pypi.org --version 99.99.99
echo Код завершения: %ERRORLEVEL%