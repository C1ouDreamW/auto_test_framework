import pytest

from base.client import ApiClient
from common.yaml_utils import read_yaml

data = read_yaml("tests/test_users/test_02.yaml")[0]
api_config = data['request']
cases = data['cases']

@pytest.mark.parametrize("case", cases,ids=[i['case_name'] for i in cases])
@pytest.mark.login
def test_02(case,set_base_url):
    api_client = ApiClient(set_base_url)
    api_client.call(api_config,case)