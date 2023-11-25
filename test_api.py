import pytest
from api import DessAPI, DessApiException
import re
from unittest.mock import patch

@pytest.fixture
def test_instance(monkeypatch):
    monkeypatch.setenv("DESS_SECRET", "test_secret")
    monkeypatch.setenv("DESS_TOKEN", "test_token")
    return DessAPI("exportDeviceDataDetail")

def test_sign(test_instance):
    assert re.match(r"\w+", test_instance.sign())

def test_call_api_with_success_with_right_params(test_instance):
    url = "http://web.dessmonitor.com/public/"
    other_params = {"param2": "value2"}
    

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-disposition": "attachment; filename=test.csv"}
        test_instance.get(**other_params)

    args, kwargs = mock_get.call_args
    assert args[0] == url
    assert 'sign' in kwargs['params'] or 'token' in kwargs['params']

def test_raise_exception_when_token_expired(test_instance):
    other_params = {"param2": "value2"}

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {"Content-type": "application/json"}
        with pytest.raises(DessApiException) as excinfo:
            test_instance.get(**other_params)
    assert excinfo.match(r"^API returned no data")
    

def test_raise_exception_when_api_down(test_instance):
    other_params = {"param2": "value2"}

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        with pytest.raises(DessApiException) as excinfo:
            test_instance.get(**other_params)
    assert excinfo.match(r"^API returned status code")
