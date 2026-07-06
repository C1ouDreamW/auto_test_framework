from base.client import ApiClient
from base.process import ProcessRunner


class TestApi:
    def test_single(self,set_base_url,auth_header,api_config,case):
        """单接口测试"""
        api_client = ApiClient(set_base_url)
        api_client.call(api_config,case,auth_header)

    def test_flow(self,set_base_url,flow_data):
        """多接口串联流程测试"""
        process_runner = ProcessRunner(set_base_url)
        process_runner.run(flow_data)