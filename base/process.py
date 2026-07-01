from base.client import ApiClient

class ProcessRunner:
    def __init__(self,base_url):
        self.client = ApiClient(base_url)

    def run(self,steps:list):
        for step in steps:
            step_name = step['step_name']
            print(f"\n========步骤：{step_name} 开始执行========")
            for case in step['cases']:
                self.client.call(step['request'],case)


