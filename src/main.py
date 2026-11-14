"""DepGraph: визуализация графа зависимостей pip-пакетов."""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse
from graph import (load_test_graph, build_graph, find_cycle,
                   print_graph, reverse_graph)
from render import to_dot, ascii_tree, render_image, show_image

PACKAGE_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")
VERSION_RE = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?$")
REQUIREMENT_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$")
URL_SCHEMES = ("http", "https")
REQUEST_TIMEOUT = 10
EXTRA_MARKER = "extra =="


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
    parser.add_argument("--reverse", action="store_true",
                        help="вывод обратных зависимостей (тестовый режим)")
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
        validate_reverse(args.reverse, args.test_mode),
    ):
        if check is not None:
            errors.append(check)
    return errors


def validate_reverse(reverse, test_mode):
    """Обратные зависимости доступны только в тестовом режиме."""
    if reverse and not test_mode:
        return "режим --reverse требует --test-mode"
    return None


def print_config(args):
    """Печатает все параметры в формате ключ-значение."""
    version = args.version if args.version is not None else "не задана"
    mode = "включен" if args.test_mode else "выключен"
    tree = "включен" if args.ascii_tree else "выключен"
    reverse = "включен" if args.reverse else "выключен"
    print(f"package: {args.package}")
    print(f"repo: {args.repo}")
    print(f"test-mode: {mode}")
    print(f"version: {version}")
    print(f"ascii-tree: {tree}")
    print(f"reverse: {reverse}")


def fetch_package_info(repo, package, version):
    """Загружает метаданные пакета; (словарь, None) или (None, ошибка)."""
    base = repo.rstrip("/")
    if base.endswith("/pypi"):
        base = base[: -len("/pypi")]
    if version is None:
        url = f"{base}/pypi/{package}/json"
    else:
        url = f"{base}/pypi/{package}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as resp:
            return json.load(resp), None
    except urllib.error.HTTPError as exc:
        return None, f"репозиторий вернул код {exc.code} для {url}"
    except urllib.error.URLError as exc:
        return None, f"нет соединения с репозиторием: {exc.reason}"
    except json.JSONDecodeError:
        return None, f"репозиторий вернул некорректный JSON: {url}"


def parse_requirement(line):
    """Разбирает строку requires_dist; (имя, спецификатор) или None."""
    if EXTRA_MARKER in line:
        return None
    base = line.split(";", 1)[0].strip()
    match = REQUIREMENT_RE.match(base)
    if match is None:
        return None
    return match.group(1), match.group(2).strip()


def get_direct_dependencies(info):
    """Извлекает прямые зависимости из метаданных пакета."""
    requires = info.get("info", {}).get("requires_dist") or []
    deps = []
    for line in requires:
        parsed = parse_requirement(line)
        if parsed is not None:
            deps.append(parsed)
    return deps


def print_dependencies(package, version, deps):
    """Печатает прямые зависимости пакета."""
    print(f"Прямые зависимости {package} {version}:")
    for name, spec in deps:
        print(f"  {name} {spec}".rstrip())


def make_real_get_deps(repo, root, version):
    """Провайдер: корень — заданная версия, остальные — последняя."""
    def get_deps(name):
        ver = version if name == root else None
        info, error = fetch_package_info(repo, name, ver)
        if error is not None:
            return []
        return [dep for dep, _ in get_direct_dependencies(info)]
    return get_deps


def show_graph(deps_graph):
    """Печатает граф и сообщает о найденном цикле."""
    print_graph(deps_graph)
    cycle = find_cycle(deps_graph)
    if cycle is not None:
        print("Обнаружен цикл: " + " -> ".join(cycle))


def show_reverse(graph, package):
    """Печатает пакеты, зависящие от данного (прямо и транзитивно)."""
    reversed_graph = reverse_graph(graph)
    reach = build_graph(lambda name: reversed_graph.get(name, []), package)
    names = sorted(set(reach) - {package})
    print(f"Обратные зависимости {package}:")
    if not names:
        print("  отсутствуют")
    for name in names:
        print(f"  {name}")


def run_test_mode(args):
    """Тестовый режим: граф из файла, DFS, циклы, обратные зависимости."""
    graph, error = load_test_graph(args.repo)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    if args.package not in graph:
        print(f"Ошибка: пакет {args.package} не найден в графе",
              file=sys.stderr)
        return 1
    if args.reverse:
        show_reverse(graph, args.package)
        return 0
    deps_graph = build_graph(lambda name: graph.get(name, []), args.package)
    show_graph(deps_graph)
    return visualize(deps_graph, args)


def run_real_mode(args):
    """Реальный режим: прямые зависимости + транзитивный граф."""
    info, error = fetch_package_info(args.repo, args.package, args.version)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    deps = get_direct_dependencies(info)
    print_dependencies(args.package, args.version, deps)
    provider = make_real_get_deps(args.repo, args.package, args.version)
    deps_graph = build_graph(provider, args.package)
    show_graph(deps_graph)
    return visualize(deps_graph, args)


def visualize(deps_graph, args):
    """Печатает DOT, ASCII-дерево и показывает изображение графа."""
    if args.ascii_tree:
        print("ASCII-дерево:")
        for line in ascii_tree(deps_graph, args.package):
            print(line)
    dot_text = to_dot(deps_graph)
    print("Описание графа на языке Graphviz:")
    print(dot_text)
    path, error = render_image(dot_text, args.package)
    if error is not None:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    print(f"Изображение графа: {path}")
    show_image(path)
    return 0


def main():
    """Точка входа: параметры, проверка, конфигурация, режимы."""
    args = build_parser().parse_args()
    errors = validate_args(args)
    if errors:
        for message in errors:
            print(f"Ошибка: {message}", file=sys.stderr)
        raise SystemExit(1)
    print_config(args)
    if args.test_mode:
        raise SystemExit(run_test_mode(args))
    raise SystemExit(run_real_mode(args))


if __name__ == "__main__":
    main()