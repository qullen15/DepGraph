"""Операции над графом зависимостей: загрузка, DFS, поиск циклов."""

import re

TEST_NAME_RE = re.compile(r"^[A-Z]+$")


def load_test_graph(path):
    """Читает файл тестового графа; (словарь, None) или (None, ошибка)."""
    graph = {}
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        return None, f"не удалось прочитать файл графа: {exc}"
    for number, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            return None, f"строка {number}: ожидался формат 'A: B C'"
        name, _, rest = line.partition(":")
        name = name.strip()
        if not TEST_NAME_RE.match(name):
            return None, f"строка {number}: имя не заглавные буквы: {name}"
        graph[name] = rest.split()
    return graph, None


def build_graph(get_deps, root):
    """Строит граф достижимых из root узлов рекурсивным DFS."""
    graph = {}
    visited = set()

    def visit(node):
        if node in visited:
            return
        visited.add(node)
        deps = get_deps(node)
        graph[node] = deps
        for dep in deps:
            visit(dep)

    visit(root)
    return graph


def find_cycle(graph):
    """Ищет цикл рекурсивным DFS; список узлов цикла или None."""
    visited = set()
    on_path = set()
    path = []

    def visit(node):
        if node in on_path:
            return path[path.index(node):] + [node]
        if node in visited:
            return None
        visited.add(node)
        on_path.add(node)
        path.append(node)
        for dep in graph.get(node, []):
            cycle = visit(dep)
            if cycle is not None:
                return cycle
        path.pop()
        on_path.discard(node)
        return None

    for node in graph:
        cycle = visit(node)
        if cycle is not None:
            return cycle
    return None


def print_graph(graph):
    """Печатает граф как список смежности."""
    for node in sorted(graph):
        deps = " ".join(graph[node])
        print(f"{node}: {deps}".rstrip())