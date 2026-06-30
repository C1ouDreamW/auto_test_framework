# Pytest自动化框架搭建笔记

> 随笔性质，记录搭建pytest自动化框架的过程，主要是为了方便自己回顾和总结。
> 测试目标项目：[iShua后端API](https://github.com/C1ouDreamW/ishua_backend)

## 1.配置文件

### 1.pytest.ini和pyproject.toml
pytest原生配置文件是pytest.ini，但ini格式文件默认都是字符串类型的配置，要使用还得转成相应格式，且不支持中文。

在现代的pytest中，推荐使用pyproject.toml作为配置文件，它支持多种数据类型，并且可以直接使用中文。

在pyproject.toml中配置pytest的方式如下：

```toml
[tool.pytest.ini_options]
# 配置选项
addopts = "-v --maxfail=5 --disable-warnings"
markers = [
    "smoke: 标记为冒烟测试",
    "regression: 标记为回归测试",
    "slow: 标记为慢速测试"
]
```
> toml文件中，规定第三方库的配置都放在[tool.xxx]下，pytest的配置放在[tool.pytest]下。
> ini_options是pytest的配置选项，所以嵌套表要写成[tool.pytest.ini_options]。

### run.py中的设置

我们将配置命令分为两批：
1. 通用的参数，比如-v、-s这些
2. 正式生成报告的参数，比如clean-alluredir、allure-severities等

通用参数是我们无论在开发时手动pytest还是正式测报告都需要的参数，

而正式生成报告的参数是我们在开发时不需要的参数，所以我们可以将通用参数放在pytest.ini或pyproject.toml中，而将正式生成报告的参数放在run.py中。

在开发过程中我们可以频繁在命令行运行pytest -v -s来调试测试用例，而在正式生成报告时我们可以运行run.py来生成报告。

## 2.fixtures

### 1.全局fixture

全局fixture是指在conftest.py中定义的fixture，可以被所有测试用例使用。

根据scope的不同，fixture可以分为function、class、module、package和session五种类型。

| scope | 执行频率 | 根 conftest 中的典型用途 |
|-------|----------|---------------------------|
| function（默认） | 每个测试函数都跑 | 临时目录、请求 session |
| class | 每个测试类跑一次 | 类共享的前置数据 |
| module | 每个 .py 文件跑一次 | 文件级公共参数 |
| session | 整个测试运行只跑一次 | 登录 token、DB 连接 |

比如在ishua中我们要对所有用例共享一个登录token，我们可以在conftest.py中定义一个session级别的fixture:
见conftest.py中的[auth_header函数](./conftest.py#L8)。

## 3.YAML格式测试用例

### 1.YAML文件
每次写测试用例都需要直接操作python文件，这样对不熟悉python的人来说是一个门槛，即使是熟悉python的人也可能会觉得繁琐。

我们可以使用YAML文件来配置一个测试用例，然后在测试用例中读取YAML文件来执行测试。

YAML文件可以自定义，本项目的格式如下：

```yaml
- api_name: 获取用户个人信息          # 接口名（顶层列表，一个文件可定义多个接口）
  request:                          # 接口级公用配置
    method: GET
    url: /users/me
  cases:                            # 测试场景列表（一个接口可以有多个测试场景）
    - case_name: 成功获取用户个人信息  # 用例名
      is_login: true                 # 是否需要登录态
      body:                          # 请求体（可选）
        key: value
      validate:                      # 断言规则
        code: 200                    # flat 断言：key = expected
        data.token: not_empty        # 嵌套路径断言：key 含点号表示逐层取值
```

> 顶层是列表（`- api_name`），一个 YAML 文件可以定义多个接口。
> `request` 放接口级公用配置（URL、method），`cases` 放每轮不同的数据（body、断言）。
> 设计原则：一个 YAML 文件 = 一个 API 接口，cases 列表 = 该接口的多个测试场景。

### 2.pytest的parametrize标记

对于上面说的YAML文件，一个接口可能包含多个case，如果一个一个地写函数会变得重复且繁琐。

parametrize是pytest提供的一个标记，用于生成多个测试用例。它可以接受一个列表或元组作为参数，每个元素都会生成一个独立的测试用例。

我们可以在测试用例中读取YAML文件，然后使用parametrize标记来生成多个测试用例。

parametrize接受三个参数：
1. **参数名**：一个字符串，表示测试函数的参数名，可以是多个参数名，用逗号分隔
2. **参数值**：一个列表或元组，每个元素都会生成一个独立的测试用例
3. **ids**（可选）：每个用例的显示名称，不写则用 case0、case1 等序号

使用方法：
```python
data = read_yaml("tests/test_users/test_01.yaml")[0]
api_config = data['request']
cases = data['cases']

# 将 cases 列表和 pytest 参数化绑定
@pytest.mark.parametrize("case", cases, ids=[c['case_name'] for c in cases])
def test_login(case, set_base_url, auth_header):
    api_client = ApiClient(set_base_url)
    api_client.call(api_config, case, auth_header)
```

> parametrize 是在**收集用例阶段**执行的，所以 YAML 必须在模块加载时就读好，不能写在函数里面。
> 有 parametrize 的情况下，pytest 自动将 cases 列表的每一项，按顺序塞进对应测试函数的参数中。

**parametrize 的等效原理**：
```python
cases = [
    {"case_name": "成功", "validate": {"code": 200}},
    {"case_name": "失败", "validate": {"code": 401}},
]

# parametrize 等价于手写两个函数：
def test_me(case={"case_name": "成功", ...}):   # 第1次调用
    ...
def test_me(case={"case_name": "失败", ...}):   # 第2次调用
    ...
```

## 3.执行引擎（ApiClient）

### 1.设计思路

测试函数里的"读 YAML - 发请求 - 跑断言"逻辑应当抽成可复用的执行引擎，放在 `base/` 目录下。

```python
# base/client.py
import requests

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def call(self, api_config, case, headers=None):
        if headers is None:
            headers = {}
        url = self.base_url + api_config['url']
        method = api_config['method']
        json_body = None
        if 'body' in case:
            json_body = case['body']
        resp = requests.request(method, url, headers=headers, json=json_body)
        for key, expected in case['validate'].items():
            actual = self.deep_get(resp.json(), key)
            if expected == 'not_empty':
                assert actual is not None and actual != ''
            elif expected is None:
                assert actual is None
            else:
                assert actual == expected
        return resp
```

### 2.deep_get：按点号路径取嵌套值

API 返回的 JSON 往往是嵌套的（如 `{"code":200, "data":{"token":"xxx"}}`），validate 用点号路径支持跨层级取值：

```python
def deep_get(self, d: dict, key_path: str):
    """按点号路径取嵌套值，'data.token' → d['data']['token']"""
    val = d
    for k in key_path.split('.'):
        if val is None:
            return None
        if isinstance(val, dict):
            val = val.get(k)
        else:
            raise KeyError(f"路径 {key_path} 在 {k} 处不是 dict")
    return val
```

> 使用 `val.get(k)` 而非 `val[k]`，因为 key 可能不存在。
> 中间节点为 `None` 时直接返回 `None`，不继续钻取，避免 `isinstance(None, dict)` 为假导致异常。
