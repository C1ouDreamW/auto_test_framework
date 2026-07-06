from base.client import ApiClient
from base.process import ProcessRunner


class TestApi:
    def test_single(self, set_base_url, auth_header, api_config, case, epic, feature, story):
        """单接口测试"""
        api_client = ApiClient(set_base_url)
        api_client.call(api_config, case, auth_header, epic, feature, story)

    def test_flow(self, set_base_url, auth_header, flow_data, epic_flow, feature_flow):
        """多接口串联流程测试"""
        process_runner = ProcessRunner(set_base_url)
        process_runner.run(flow_data, auth_header, epic_flow, feature_flow)
