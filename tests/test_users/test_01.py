import pytest
import requests
from common.read_yaml import read_yaml

data = read_yaml("tests/test_users/test_01.yaml")[0]
api_config = data['request']
cases = data['cases']

# ----- login -----
@pytest.mark.parametrize("case", cases)
@pytest.mark.login
def test_login(auth_header,case):
    url = api_config['url']
    method = api_config['method']
    resp = requests.request(method,url,headers=auth_header)
    for key, expected in case["validate"].items():
        actual = resp.json().get(key)
        assert actual == expected


