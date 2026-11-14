@echo off
chcp 65001 >nul
echo === 1. Тестовый граф: DOT + PNG + ASCII ===
py src/main.py --package A --repo tests/data/graph.txt --test-mode --ascii-tree
echo Код: %ERRORLEVEL%
echo === 2. Цикл в ASCII-дереве ===
py src/main.py --package A --repo tests/data/cycle.txt --test-mode --ascii-tree
echo Код: %ERRORLEVEL%
echo === 3. Пакет requests ===
py src/main.py --package requests --repo https://pypi.org --version 2.31.0 --ascii-tree
echo Код: %ERRORLEVEL%
echo === 4. Пакет flask ===
py src/main.py --package flask --repo https://pypi.org --version 3.0.0 --ascii-tree
echo Код: %ERRORLEVEL%
echo === 5. Пакет click ===
py src/main.py --package click --repo https://pypi.org --version 8.1.7 --ascii-tree
echo Код: %ERRORLEVEL%