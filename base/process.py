import allure

from base.client import ApiClient
from common.logger import logger


class ProcessRunner:
    def __init__(self,base_url):
        self.client = ApiClient(base_url)

    def run(self,steps:list):
        logger.info("======== 多接口任务开始执行 ========")
        cnt = 0
        for step in steps:

            cnt += 1
            step_name = step['step_name']
            with allure.step(step['step_name']):
                logger.info(f"======== 步骤{cnt}：{step_name} 开始执行 ========")
                for case in step['cases']:
                    self.client.call(step['request'],case)

        logger.info("======== 多接口任务执行完毕 ========")


