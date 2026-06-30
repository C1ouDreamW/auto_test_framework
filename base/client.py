import requests


class ApiClient:
    def __init__(self,base_url):
        self.base_url = base_url

    def call(self,api_config,case,headers):
        url = self.base_url + api_config['url']
        method = api_config['method']
        resp = requests.request(method, url, headers=headers) if case['is_login'] else requests.request(method, url)
        for key, expected in case["validate"].items():
            actual = resp.json().get(key)
            assert actual == expected
        return resp
