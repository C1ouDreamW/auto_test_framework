import configparser
from conf.setting import FILE_PATH


class ConfigReader:
    def __init__(self):
        self.conf = configparser.ConfigParser()
        self.conf.read(FILE_PATH['CONFIG'], encoding='utf-8')

    def get(self, section, key):
        """
        获取配置信息
        :param section: 节
        :param key: 键
        :return: 值
        """
        return self.conf.get(section, key)
