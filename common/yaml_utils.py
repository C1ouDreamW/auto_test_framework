import yaml
from pathlib import Path

def read_yaml(file_path):
    """
    读取yaml文件
    :param file_path: 文件地址
    :return: 返回yaml文件内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data

def append_yaml(file_path,new_data:dict):
    """
    追加写入yaml文件
    :param file_path: 文件地址
    :param new_data: 要插入的键值对
    """
    path = Path(file_path)
    path.touch()
    current_data = {}
    
    with path.open("r",encoding="utf-8") as f:
        current_data = yaml.safe_load(f) or {}

    for key,value in new_data.items():
        current_data[key] = value

    with path.open("w",encoding="utf-8") as f:
        yaml.safe_dump(current_data,f,allow_unicode=True)

def clear_yaml(file_path):
    path = Path(file_path)
    path.write_text("",encoding="utf-8")