@echo off
chcp 65001 >nul
echo === 1. Ромб ===
py src/main.py --package A --repo tests/data/graph.txt --test-mode
echo Код: %ERRORLEVEL%
echo === 2. Цикл ===
py src/main.py --package A --repo tests/data/cycle.txt --test-mode
echo Код: %ERRORLEVEL%
echo === 3. Глубокий ===
py src/main.py --package A --repo tests/data/deep.txt --test-mode
echo Код: %ERRORLEVEL%
echo === 4. Ошибка формата ===
py src/main.py --package A --repo tests/data/bad.txt --test-mode
echo Код: %ERRORLEVEL%
echo === 5. Пакет не найден ===
py src/main.py --package Z --repo tests/data/graph.txt --test-mode
echo Код: %ERRORLEVEL%