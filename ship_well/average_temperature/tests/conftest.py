import requests
from unittest.mock import MagicMock

from pytest import fixture


@fixture
def requests_mock_get(monkeypatch):
    response = MagicMock()
    get = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "get", get)
    return get, response


@fixture
def requests_mock_post(monkeypatch):
    response = MagicMock()
    post = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "post", post)
    return post, response
