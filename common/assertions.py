from common.deep_get import deep_get
from common.logger import logger


class AssertEngine:
    def run(self,validate_dict:dict,resp_dict:dict):
        failed = 0
        for key,expected in validate_dict.items():
            actual = deep_get(resp_dict,key)
            is_ok = self._check(actual,expected)
            if is_ok:
                logger.info(f"--[断言通过]-- {key}")
            else:
                failed +=1
                logger.error(f"  [断言失败] {key}: 预期={expected}, 实际={actual}")
        if failed>0:
            raise AssertionError(f"{failed}/{len(validate_dict)} 条断言失败")


    def _check(self, actual, expected):
        if expected == "not_empty":
            return actual is not None and actual !=""
        elif expected is None:
            return actual is None
        else:
            return actual == expected

