import pytest
from base.process import ProcessRunner
from common.yaml_utils import read_yaml

data = read_yaml("tests/test_users/work_flow.yaml")


@pytest.mark.test
def test_user_flow(set_base_url):
    process_runner = ProcessRunner(set_base_url)
    process_runner.run(data)


