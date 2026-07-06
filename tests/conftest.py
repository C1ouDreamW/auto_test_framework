from pathlib import Path

import pytest

from common.yaml_utils import read_yaml

MODULE_MAP = {
    "test_users": "用户管理",
    "test_question_banks": "题库管理",
    "test_bank_nodes": "题库树节点",
    "test_questions": "试题管理",
    "test_practice": "刷题",
    "test_wrong_questions": "错题本",
    "work_flows": "业务流程",
    "test_admin": "管理端",
}


def _module_name(parent_dir: str) -> str:
    return MODULE_MAP.get(parent_dir, parent_dir.replace("test_", "").replace("_", " ").title())


def pytest_generate_tests(metafunc):
    here = Path(__file__).parent

    single_params = []
    single_ids = []
    flow_params = []
    flow_ids = []

    for yf in sorted(here.rglob("*.yaml")):
        if yf.name.startswith("_"):
            continue
        data = read_yaml(str(yf))
        parent_dir = yf.parent.name
        default_feature = _module_name(parent_dir)

        if isinstance(data, list) and len(data) == 1 and "cases" in data[0]:
            api_config = data[0]["request"]
            cases = data[0]["cases"]
            api_name = data[0].get("api_name", yf.stem)
            epic = data[0].get("epic", default_feature)
            feature = data[0].get("feature", default_feature)

            for case in cases:
                story = case.get("story", case.get("case_name", "未命名"))
                mark_name = case.get("mark")
                marks = [getattr(pytest.mark, mark_name)] if mark_name else []

                single_params.append(
                    pytest.param(api_config, case, epic, feature, story, marks=marks)
                )
                single_ids.append(case.get("case_name", "未命名"))

        elif isinstance(data, list) and len(data) > 1 and "step_name" in data[0]:
            epic = data[0].get("epic", default_feature)
            feature = data[0].get("feature", default_feature)
            flow_params.append(pytest.param(data, epic, feature))
            flow_ids.append(yf.stem)

    if "api_config" in metafunc.fixturenames and "case" in metafunc.fixturenames:
        metafunc.parametrize("api_config,case,epic,feature,story", single_params, ids=single_ids)
    if "flow_data" in metafunc.fixturenames:
        metafunc.parametrize("flow_data,epic_flow,feature_flow", flow_params, ids=flow_ids)
