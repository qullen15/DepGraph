"""Юнит-тесты этапа 5: DOT, ASCII-дерево, рендер изображения."""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import render
from render import to_dot, ascii_tree, render_image

EXPECTED_LINES = 3


class TestToDot:
    """Формирование текста на языке Graphviz."""

    def test_contains_nodes_and_edges(self):
        text = to_dot({"A": ["B"], "B": []})
        assert "digraph dependencies {" in text
        assert '"A" -> "B";' in text
        assert text.strip().endswith("}")

    def test_empty_graph(self):
        assert "digraph" in to_dot({})


class TestAsciiTree:
    """Построение ASCII-дерева."""

    def test_chain(self):
        lines = ascii_tree({"A": ["B"], "B": ["C"], "C": []}, "A")
        assert lines[0] == "A"
        assert "B" in lines[1]
        assert "C" in lines[2]

    def test_cycle_marked(self):
        lines = ascii_tree({"A": ["B"], "B": ["A"]}, "A")
        assert any("цикл" in line for line in lines)

    def test_branches(self):
        lines = ascii_tree({"A": ["B", "C"], "B": [], "C": []}, "A")
        assert len(lines) == EXPECTED_LINES


class TestRenderImage:
    """Рендер изображения без реального вызова Graphviz."""

    def test_missing_graphviz(self, monkeypatch, tmp_path):
        monkeypatch.setattr(render, "IMAGE_DIR", str(tmp_path))

        def boom(*args, **kwargs):
            raise FileNotFoundError()

        monkeypatch.setattr(render.subprocess, "run", boom)
        path, error = render_image("digraph {}", "X")
        assert path is None
        assert "Graphviz" in error

    def test_success(self, monkeypatch, tmp_path):
        monkeypatch.setattr(render, "IMAGE_DIR", str(tmp_path))
        monkeypatch.setattr(
            render.subprocess, "run",
            lambda *a, **k: subprocess.CompletedProcess(a, 0))
        path, error = render_image("digraph {}", "X")
        assert error is None
        assert path.endswith("X.png")