import requests


class ApiClient:
    def __init__(self,base_url):
        self.base_url = base_url

    def deep_get(self, d: dict, key_path: str):
        """按点号路径取嵌套值，'data.token' → d['data']['token']"""
        val = d
        for k in key_path.split('.'):
            if val is None:
                return None
            if isinstance(val, dict):
                val = val.get(k)
            else:
                raise KeyError(f"路径 {key_path} 在 {k} 处不是 dict")
        return val

    def call(self, api_config, case, headers=None):
        if headers is None:
            headers = {}
        url = self.base_url + api_config['url']
        method = api_config['method']
        json = None
        if 'json' in case:
            json = case['json']
        resp = requests.request(method, url, headers=headers,json=json) if case['is_login'] else requests.request(method, url,json=json)
        for key, expected in case["validate"].items():
            actual = self.deep_get(resp.json(), key)  # key = "data.token"
            if expected == 'not_empty':
                assert actual is not None and actual != ''
            elif expected is None:
                assert actual is None
            else:
                assert actual == expected
        return resp
