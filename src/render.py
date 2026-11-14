"""Визуализация графа: язык Graphviz, рендер изображения, ASCII-дерево."""

import os
import subprocess
import sys

DOT_HEADER = "digraph dependencies {"
DOT_FOOTER = "}"
IMAGE_DIR = "out"
RENDER_TIMEOUT = 30


def to_dot(graph):
    """Формирует описание графа на языке диаграмм Graphviz."""
    lines = [DOT_HEADER, "    rankdir=LR;"]
    for node in sorted(graph):
        lines.append(f'    "{node}";')
        for dep in sorted(graph[node]):
            lines.append(f'    "{node}" -> "{dep}";')
    lines.append(DOT_FOOTER)
    return "\n".join(lines)


def ascii_tree(graph, root):
    """Строит строки ASCII-дерева зависимостей от корневого пакета."""
    lines = [root]

    def walk(node, prefix, path):
        deps = graph.get(node, [])
        for index, dep in enumerate(deps):
            last = index == len(deps) - 1
            branch = "`-- " if last else "|-- "
            if dep in path:
                lines.append(f"{prefix}{branch}{dep} (цикл)")
                continue
            lines.append(f"{prefix}{branch}{dep}")
            tail = "    " if last else "|   "
            walk(dep, prefix + tail, path | {dep})

    walk(root, "", {root})
    return lines


def render_image(dot_text, name):
    """Рендерит DOT в PNG; возвращает (путь, None) или (None, ошибка)."""
    os.makedirs(IMAGE_DIR, exist_ok=True)
    dot_path = os.path.join(IMAGE_DIR, f"{name}.dot")
    png_path = os.path.join(IMAGE_DIR, f"{name}.png")
    with open(dot_path, "w", encoding="utf-8") as fh:
        fh.write(dot_text)
    try:
        subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path],
                       check=True, capture_output=True,
                       timeout=RENDER_TIMEOUT)
    except FileNotFoundError:
        return None, "Graphviz не установлен: команда dot не найдена"
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip()
        return None, f"ошибка рендера Graphviz: {detail}"
    except subprocess.TimeoutExpired:
        return None, "превышено время рендера графа"
    return png_path, None


def show_image(path):
    """Открывает изображение системной программой просмотра."""
    if sys.platform.startswith("win"):
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)