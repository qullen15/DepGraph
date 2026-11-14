@echo off
chcp 65001 >nul
echo === 1. Обратные зависимости D (ромб) ===
py src/main.py --package D --repo tests/data/graph.txt --test-mode --reverse
echo Код: %ERRORLEVEL%
echo === 2. У корня A обратных нет ===
py src/main.py --package A --repo tests/data/graph.txt --test-mode --reverse
echo Код: %ERRORLEVEL%
echo === 3. Две ветви зависимых ===
py src/main.py --package D --repo tests/data/reverse.txt --test-mode --reverse
echo Код: %ERRORLEVEL%
echo === 4. Граф с циклом ===
py src/main.py --package A --repo tests/data/cycle.txt --test-mode --reverse
echo Код: %ERRORLEVEL%
echo === 5. Ошибка: --reverse без --test-mode ===
py src/main.py --package requests --repo https://pypi.org --version 2.31.0 --reverse
echo Код: %ERRORLEVEL%