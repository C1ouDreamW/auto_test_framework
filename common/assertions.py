

class AssertEngine:
    def run(self,validate_dict:dict,resp_dict:dict):
        failed = 0
        for key,expected in validate_dict.items():
            actual = self._deep_get(resp_dict,key)
            is_ok = self._check(actual,expected)
            if is_ok:
                print(f"--[断言通过]--{key}")
            else:
                failed +=1
                print(f"  [断言失败] {key}: 预期={expected}, 实际={actual}")
        if failed>0:
            raise AssertionError(f"{failed}/{len(validate_dict)} 条断言失败")


    def _deep_get(self,d:dict,path:str):
        now = d
        for i in path.split('.'):
            if now is None:
                return None
            if isinstance(now,dict):
                now = now.get(i)
            else:
                raise KeyError(f"路径 {path} 在 {i} 处不是dict")
        return now

    def _check(self, actual, expected):
        if expected == "not_empty":
            return actual is not None and actual !=""
        elif expected is None:
            return actual is None
        else:
            return actual == expected

