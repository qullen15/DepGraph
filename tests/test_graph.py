"""Юнит-тесты этапа 3: граф, DFS, циклы."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from graph import load_test_graph, build_graph, find_cycle


class TestLoadTestGraph:
    def test_ok(self, tmp_path):
        p = tmp_path / "g.txt"
        p.write_text("A: B C\nB:\n", encoding="utf-8")
        g, err = load_test_graph(str(p))
        assert err is None
        assert g == {"A": ["B", "C"], "B": []}

    def test_bad_format(self, tmp_path):
        p = tmp_path / "g.txt"
        p.write_text("A B\n", encoding="utf-8")
        g, err = load_test_graph(str(p))
        assert g is None and err

    def test_lowercase(self, tmp_path):
        p = tmp_path / "g.txt"
        p.write_text("a: B\n", encoding="utf-8")
        g, err = load_test_graph(str(p))
        assert g is None and err

    def test_missing(self, tmp_path):
        g, err = load_test_graph(str(tmp_path / "no.txt"))
        assert g is None and err


class TestBuildGraph:
    def test_transitive(self):
        g = {"A": ["B"], "B": ["C"], "C": []}
        result = build_graph(lambda n: g.get(n, []), "A")
        assert set(result) == {"A", "B", "C"}

    def test_cycle_terminates(self):
        g = {"A": ["B"], "B": ["A"]}
        result = build_graph(lambda n: g.get(n, []), "A")
        assert set(result) == {"A", "B"}


class TestFindCycle:
    def test_no_cycle(self):
        assert find_cycle({"A": ["B"], "B": []}) is None

    def test_cycle(self):
        g = {"A": ["B"], "B": ["D"], "D": ["A"]}
        assert find_cycle(g) == ["A", "B", "D", "A"]

    def test_cross_edge_not_cycle(self):
        g = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        assert find_cycle(g) is None