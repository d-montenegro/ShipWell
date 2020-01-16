import requests
from unittest.mock import MagicMock

from pytest import fixture


@fixture
def requests_mock(monkeypatch):
    response = MagicMock()
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    return get, response
