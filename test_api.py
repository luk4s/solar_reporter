import pytest
from api import DessAPI
import re
from unittest.mock import patch

@pytest.fixture
def test_instance(monkeypatch):
    monkeypatch.setenv("DESS_SECRET", "test_secret")
    monkeypatch.setenv("DESS_TOKEN", "test_token")
    return DessAPI("exportDeviceDataDetail")

def test_sign(test_instance):
    assert re.match(r"\w+", test_instance.sign())

@pytest.fixture
def mock_requests_get():
    with patch('requests.get') as mock_get:
        yield mock_get

def test_function_to_test_with_params(mock_requests_get, test_instance):
    url = "http://web.dessmonitor.com/public/"
    other_params = {"param2": "value2"}

    test_instance.get(**other_params)

    # Check that requests.get was called with the right parameters
    args, kwargs = mock_requests_get.call_args
    assert args[0] == url
    assert 'sign' in kwargs['params'] or 'token' in kwargs['params']