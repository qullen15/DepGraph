"""Юнит-тесты этапа 2: сбор прямых зависимостей."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import (parse_requirement, get_direct_dependencies,
                  fetch_package_info, print_dependencies)


class TestParseRequirement:
    """Разбор строки requires_dist."""

    def test_name_and_spec(self):
        result = parse_requirement("urllib3>=1.21.1,<3")
        assert result == ("urllib3", ">=1.21.1,<3")

    def test_name_only(self):
        assert parse_requirement("certifi") == ("certifi", "")

    def test_space_before_spec(self):
        result = parse_requirement("Werkzeug >=3.0.0")
        assert result == ("Werkzeug", ">=3.0.0")

    def test_extra_skipped(self):
        line = 'PySocks>=1.5.6; extra == "socks"'
        assert parse_requirement(line) is None

    def test_env_marker_stripped(self):
        result = parse_requirement('foo>=1; python_version<"3.8"')
        assert result == ("foo", ">=1")


class TestGetDirectDependencies:
    """Извлечение прямых зависимостей из метаданных."""

    def test_filters_extras(self):
        info = {"info": {"requires_dist": ["a>=1", 'b; extra == "x"', "c"]}}
        assert get_direct_dependencies(info) == [("a", ">=1"), ("c", "")]

    def test_missing_fields(self):
        assert get_direct_dependencies({}) == []
        assert get_direct_dependencies({"info": {}}) == []


class FakeResponse:
    """Поддельный HTTP-ответ, чтобы тест не ходил в сеть."""

    def __init__(self, payload):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TestFetchPackageInfo:
    """Загрузка метаданных: успех и ошибки, без реальной сети."""

    def test_success(self, monkeypatch):
        payload = {"info": {"requires_dist": ["a>=1"]}}
        monkeypatch.setattr(
            urllib.request, "urlopen",
            lambda url, timeout=None: FakeResponse(payload))
        info, err = fetch_package_info("https://pypi.org", "x", "1.0")
        assert err is None
        assert info["info"]["requires_dist"] == ["a>=1"]

    def test_http_error(self, monkeypatch):
        def boom(url, timeout=None):
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
        monkeypatch.setattr(urllib.request, "urlopen", boom)
        info, err = fetch_package_info("https://pypi.org", "nope", "9.9")
        assert info is None
        assert "404" in err

    def test_url_error(self, monkeypatch):
        def boom(url, timeout=None):
            raise urllib.error.URLError("dns fail")
        monkeypatch.setattr(urllib.request, "urlopen", boom)
        info, err = fetch_package_info("https://pypi.org", "x", "1.0")
        assert info is None
        assert err is not None


class TestPrintDependencies:
    """Вывод прямых зависимостей."""

    def test_prints_names(self, capsys):
        deps = [("urllib3", ">=1.21.1,<3"), ("certifi", "")]
        print_dependencies("requests", "2.31.0", deps)
        out = capsys.readouterr().out
        assert "urllib3 >=1.21.1,<3" in out
        assert "certifi" in out