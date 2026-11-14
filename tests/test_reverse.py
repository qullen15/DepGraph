"""Юнит-тесты этапа 4: обратные зависимости."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph import reverse_graph, build_graph
from main import validate_reverse, main


class TestReverseGraph:
    """Обращение рёбер графа."""

    def test_simple(self):
        assert reverse_graph({"A": ["B"], "B": []}) == {"A": [], "B": ["A"]}

    def test_multiple_dependents(self):
        graph = {"A": ["C"], "B": ["C"], "C": []}
        assert reverse_graph(graph) == {"A": [], "B": [], "C": ["A", "B"]}

    def test_unknown_node_added(self):
        assert reverse_graph({"A": ["Z"]}) == {"A": [], "Z": ["A"]}


class TestReverseTraversal:
    """Обход по обращённому графу."""

    def test_transitive_dependents(self):
        rev = reverse_graph({"A": ["B"], "B": ["C"], "C": []})
        result = build_graph(lambda n: rev.get(n, []), "C")
        assert set(result) == {"A", "B", "C"}

    def test_no_dependents(self):
        rev = reverse_graph({"A": ["B"], "B": []})
        result = build_graph(lambda n: rev.get(n, []), "A")
        assert set(result) == {"A"}

    def test_cycle_terminates(self):
        rev = reverse_graph({"A": ["B"], "B": ["A"]})
        result = build_graph(lambda n: rev.get(n, []), "A")
        assert set(result) == {"A", "B"}


class TestValidateReverse:
    """Проверка сочетания параметров."""

    def test_requires_test_mode(self):
        assert validate_reverse(True, False) is not None

    def test_ok_in_test_mode(self):
        assert validate_reverse(True, True) is None

    def test_off_ok(self):
        assert validate_reverse(False, False) is None


class TestReverseMode:
    """Вывод обратных зависимостей через точку входа."""

    def test_prints_dependents(self, tmp_path, capsys, monkeypatch):
        script = tmp_path / "g.txt"
        script.write_text("A: B\nB: C\nC:\n", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", [
            "main.py", "--package", "C", "--repo", str(script),
            "--test-mode", "--reverse"])
        with pytest.raises(SystemExit) as exc:
            main()
        out = capsys.readouterr().out
        assert exc.value.code == 0
        assert "Обратные зависимости C:" in out