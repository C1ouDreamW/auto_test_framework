# 这里是全局fixture
import pytest
import requests

from common.extract import clear_extract


@pytest.fixture(scope="session")
def set_base_url():
    base_url = "http://localhost:8080/api/v1"
    return base_url

@pytest.fixture(scope="session",autouse=True)
def clear_extract_yaml():
    clear_extract()

@pytest.fixture(scope="session")
def auth_header(set_base_url):
    """
    全局登录fixture返回header键值对
    :return: 返回{Authorization":"Bearer <token>}
    """
    resp = requests.post(set_base_url+"/users/login",json={
        'username':'testuser',
        'password':'123456'
    })
    token = resp.json()['data']['token']
    return {"Authorization":"Bearer "+token}



def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时触发的钩子函数，用于解决 Allure 报告中参数化中文乱码的问题
    """
    for item in items:
        # 修改用例的名称属性
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        # 修改用例的节点 ID 属性
        item._nodeid = item._nodeid.encode("utf-8").decode("unicode_escape")