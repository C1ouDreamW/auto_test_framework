from pathlib import Path
from common.yaml_utils import read_yaml


def pytest_generate_tests(metafunc):
    here = Path(__file__).parent

    single_params = []
    single_ids = []
    flow_params = []
    flow_ids = []

    # =====收集所有yaml用例信息并分类
    for yf in sorted(here.rglob("*.yaml")):
        data = read_yaml(str(yf))
        if isinstance(data,list) and len(data) == 1  and 'cases' in data[0]:
            # 单接口测试
            api_config = data[0]['request']
            cases = data[0]['cases']
            api_name = data[0].get('api_name',yf.stem) # 获取api名，默认用文件名
            for case in cases:
                single_params.append((api_config,case))
                single_ids.append(case.get('case_name','未命名'))
        elif isinstance(data,list) and len(data) > 1 and 'step_name' in data[0]:
            # 多接口测试
            flow_params.append(data)
            flow_ids.append(yf.stem)
    # =====开始注入=====
    if 'api_config' in metafunc.fixturenames and 'case' in metafunc.fixturenames:
        metafunc.parametrize('api_config,case',single_params,ids=single_ids)
    if 'flow_data' in metafunc.fixturenames:
        metafunc.parametrize('flow_data',flow_params,ids=flow_ids)
