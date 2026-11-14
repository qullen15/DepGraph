@echo off
chcp 65001 >nul
echo === 1. Корректные параметры (реальный режим) ===
py src/main.py --package requests --repo https://pypi.org/pypi --version 2.31.0
echo Код завершения: %ERRORLEVEL%

echo === 2. Тестовый режим с файлом графа ===
py src/main.py --package A --repo tests/data/graph.txt --test-mode --ascii-tree
echo Код завершения: %ERRORLEVEL%

echo === 3. Ошибка: некорректное имя пакета ===
py src/main.py --package "bad name" --repo https://pypi.org/pypi --version 2.31.0
echo Код завершения: %ERRORLEVEL%

echo === 4. Ошибка: нет версии в реальном режиме ===
py src/main.py --package requests --repo https://pypi.org/pypi
echo Код завершения: %ERRORLEVEL%

echo === 5. Ошибка: несуществующий тестовый файл ===
py src/main.py --package A --repo tests/data/nope.txt --test-mode
echo Код завершения: %ERRORLEVEL%

echo === 6. Ошибка: значение у флага --ascii-tree ===
py src/main.py --package A --repo tests/data/graph.txt --test-mode --ascii-tree yes
echo Код завершения: %ERRORLEVEL%