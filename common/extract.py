from pathlib import Path

from common.deep_get import deep_get
from common.yaml_utils import *

EXTRACT_FILE_PATH = Path(__file__).resolve().parent.parent / "extract.yaml"

def write_extract(data:dict):
    append_yaml(EXTRACT_FILE_PATH,data)

def read_extract(key_path):
    data = read_yaml(EXTRACT_FILE_PATH)
    print(data)
    return deep_get(data,key_path)

def clear_extract():
    clear_yaml(EXTRACT_FILE_PATH)




# -----测试-----
if __name__ == "__main__":
    test_data = {
        "测试1":1,
        "测试2":"数据",
        "测试3":{"内部1":"结果1"},
    }
    write_extract(test_data)
    print(read_extract("测试3.内部1"))