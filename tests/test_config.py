"""Юнит-тесты этапа 1: параметры командной строки и их проверка."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import (build_parser, validate_package, validate_version,
                  validate_repo, main)

USAGE_ERROR_CODE = 2


class TestBuildParser:
    """Разбор параметров командной строки."""

    def test_parses_all_options(self):
        args = build_parser().parse_args(
            ["--package", "requests", "--repo", "https://pypi.org/pypi",
             "--version", "2.31.0", "--test-mode", "--ascii-tree"])
        assert args.package == "requests"
        assert args.repo == "https://pypi.org/pypi"
        assert args.version == "2.31.0"
        assert args.test_mode is True
        assert args.ascii_tree is True

    def test_defaults(self):
        args = build_parser().parse_args(
            ["--package", "requests", "--repo", "https://pypi.org/pypi"])
        assert args.version is None
        assert args.test_mode is False
        assert args.ascii_tree is False

    def test_missing_required_exits(self):
        with pytest.raises(SystemExit) as exc:
            build_parser().parse_args([])
        assert exc.value.code == USAGE_ERROR_CODE


class TestValidators:
    """Проверка значений параметров."""

    def test_valid_package(self):
        assert validate_package("requests") is None
        assert validate_package("my-pkg_2") is None

    def test_invalid_package(self):
        assert validate_package("-bad") is not None
        assert validate_package("bad name") is not None

    def test_version_ok(self):
        assert validate_version("2.31.0", False) is None
        assert validate_version("1.0rc1", False) is None

    def test_version_bad_format(self):
        assert validate_version("abc", False) is not None

    def test_version_required_in_real_mode(self):
        assert validate_version(None, False) is not None
        assert validate_version(None, True) is None

    def test_repo_url_ok(self):
        assert validate_repo("https://pypi.org/pypi", False) is None

    def test_repo_url_bad(self):
        assert validate_repo("not-a-url", False) is not None

    def test_repo_test_file_ok(self, tmp_path):
        graph = tmp_path / "graph.txt"
        graph.write_text("A: B\n", encoding="utf-8")
        assert validate_repo(str(graph), True) is None

    def test_repo_test_file_missing(self, tmp_path):
        missing = str(tmp_path / "nope.txt")
        assert validate_repo(missing, True) is not None


class TestMain:
    """Точка входа: вывод конфигурации и коды завершения."""

    def test_prints_config(self, capsys, monkeypatch):
        monkeypatch.setattr(
            sys, "argv",
            ["main.py", "--package", "requests",
             "--repo", "https://pypi.org/pypi", "--version", "2.31.0"])
        with pytest.raises(SystemExit) as exc:
            main()
        out = capsys.readouterr().out
        assert exc.value.code == 0
        assert "package: requests" in out
        assert "version: 2.31.0" in out
        assert "ascii-tree: выключен" in out

    def test_bad_params_exit_one(self, capsys, monkeypatch):
        monkeypatch.setattr(
            sys, "argv",
            ["main.py", "--package", "bad name",
             "--repo", "https://pypi.org/pypi", "--version", "2.31.0"])
        with pytest.raises(SystemExit) as exc:
            main()
        err = capsys.readouterr().err
        assert exc.value.code == 1
        assert "некорректное имя пакета" in err