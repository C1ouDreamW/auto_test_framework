import yaml

def read_yaml(file_path):
    """
    读取yaml文件
    :param file_path: 文件地址
    :return: 返回yaml文件内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data