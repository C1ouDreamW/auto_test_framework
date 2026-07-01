import json
import requests

from common.functions import DynamicFunctions


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
        if 'json' in case:
            case['json'] = self.replace_load(case['json'])
        #发送请求
        kwargs = {
            'method':method,
            'url':url,
            'headers':headers if case['is_login'] else None,
            'json':case.get('json')
        }
        resp = requests.request(**kwargs)

        # 断言判断
        for key, expected in case["validate"].items():
            actual = self.deep_get(resp.json(), key)  # key = "data.token"
            if expected == 'not_empty':
                assert actual is not None and actual != ''
            elif expected is None:
                assert actual is None
            else:
                assert actual == expected
        return resp

    def replace_load(self, data):
        """
        解析 ${函数名(参数)} 模板，反射调用 DynamicFunctions 替换
        输入yaml原始数据，输出对应的替换后的数据
        :param data:
        :return:
        """
        if data is None:
            return None

        str_data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)

        for _ in range(str_data.count('${')):
            if '${' in str_data and '}' in str_data:
                start = str_data.index('$')
                end = str_data.index('}', start)
                ref_all = str_data[start:end + 1]
                func_name = ref_all[2:ref_all.index('(')]
                func_params = ref_all[ref_all.index('(') + 1:ref_all.index(')')]

                result = getattr(DynamicFunctions(), func_name)(
                    *func_params.split(',') if func_params else ""
                )
                str_data = str_data.replace(ref_all, str(result))

        return json.loads(str_data) if isinstance(data, dict) else str_data
