import random

from common.extract import read_extract


class DynamicFunctions:
    """
    动态函数库，YAML中通过 ${函数名} 调用
    """
    def get_extract_data(self,key_path):
        return read_extract(key_path)

    def random_string(self, length=8):
        """返回指定长度的随机字母数字串"""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(random.choice(chars) for _ in range(int(length)))
