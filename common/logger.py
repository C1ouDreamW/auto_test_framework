import logging
from datetime import datetime

from conf.setting import FILE_PATH

LOG_PATH = FILE_PATH['LOG']
LOG_PATH.mkdir(parents=True,exist_ok=True)
LOG_FILE = LOG_PATH / f"test.{datetime.now():%Y%m%d}.log"

def get_logger(name: str = "apitest"):
    logger = logging.getLogger(name)
    if logger.handlers:          # 防止重复添加
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # 文件 handler
    fh = logging.FileHandler(LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # 控制台 handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


logger = get_logger()