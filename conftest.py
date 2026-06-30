# 这里是全局fixture
import pytest
import requests

baseUrl = "http://localhost:8080/api/v1"

@pytest.fixture(scope="session")
def auth_header():
    """
    全局登录fixture返回header键值对
    :return: 返回{Authorization":"Bearer <token>}
    """
    resp = requests.post(baseUrl+"/users/login",json={
        'username':'testuser',
        'password':'123456'
    })
    token = resp.json()['data']['token']
    return {"Authorization":"Bearer "+token}
