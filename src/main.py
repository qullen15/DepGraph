"""DepGraph: визуализация графа зависимостей pip-пакетов."""

import argparse
import os
import re
import sys
from urllib.parse import urlparse

PACKAGE_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
VERSION_RE = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?$")
URL_SCHEMES = ("http", "https")


def build_parser():
    """Создаёт парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="DepGraph",
        description="Визуализация графа зависимостей pip-пакетов.",
    )
    parser.add_argument("--package", required=True, metavar="NAME",
                        help="имя анализируемого пакета")
    parser.add_argument("--repo", required=True, metavar="URL|PATH",
                        help="URL репозитория или путь к тестовому файлу")
    parser.add_argument("--test-mode", action="store_true",
                        help="режим работы с тестовым репозиторием")
    parser.add_argument("--version", metavar="VER", default=None,
                        help="версия пакета (обязательна в реальном режиме)")
    parser.add_argument("--ascii-tree", action="store_true",
                        help="вывод зависимостей в формате ASCII-дерева")
    return parser


def validate_package(name):
    """Проверяет имя пакета; возвращает текст ошибки или None."""
    if not PACKAGE_RE.match(name):
        return f"некорректное имя пакета: {name}"
    return None


def validate_version(version, test_mode):
    """Проверяет версию пакета; возвращает текст ошибки или None."""
    if version is None:
        if not test_mode:
            return "в реальном режиме требуется параметр --version"
        return None
    if not VERSION_RE.match(version):
        return f"некорректная версия пакета: {version}"
    return None


def validate_repo(repo, test_mode):
    """Проверяет адрес репозитория; возвращает текст ошибки или None."""
    if test_mode:
        if not os.path.isfile(repo):
            return f"файл тестового репозитория не найден: {repo}"
        return None
    parts = urlparse(repo)
    if parts.scheme not in URL_SCHEMES or not parts.netloc:
        return f"некорректный URL репозитория: {repo}"
    return None


def validate_args(args):
    """Проверяет все параметры; возвращает список текстов ошибок."""
    errors = []
    for check in (
        validate_package(args.package),
        validate_version(args.version, args.test_mode),
        validate_repo(args.repo, args.test_mode),
    ):
        if check is not None:
            errors.append(check)
    return errors


def print_config(args):
    """Печатает все параметры в формате ключ-значение."""
    version = args.version if args.version is not None else "не задана"
    mode = "включен" if args.test_mode else "выключен"
    tree = "включен" if args.ascii_tree else "выключен"
    print(f"package: {args.package}")
    print(f"repo: {args.repo}")
    print(f"test-mode: {mode}")
    print(f"version: {version}")
    print(f"ascii-tree: {tree}")


def main():
    """Точка входа: разбор параметров, проверка, вывод конфигурации."""
    args = build_parser().parse_args()
    errors = validate_args(args)
    if errors:
        for message in errors:
            print(f"Ошибка: {message}", file=sys.stderr)
        raise SystemExit(1)
    print_config(args)
    raise SystemExit(0)


if __name__ == "__main__":
    main()