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

## 4.执行引擎（ApiClient）

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

## 5.动态函数机制

### 1.为什么需要

YAML 是静态文本，无法自行动态生成值（时间戳、随机字符串等），更不能跨用例传数据（前一个用例的 token 给后面用）。

解决办法：在 YAML 中写 `${函数名(参数)}` 占位符，运行时由 Python 反射调用对应函数，把返回值填回去。

### 2.核心原理：replace_load 三步走

```
"token: ${get_extract_data(token)}"
  │
  ├─ 1. 字符串定位    → 找到 "${get_extract_data(token)}"
  ├─ 2. 拆解函数名/参  → func_name="get_extract_data", func_params="token"
  └─ 3. 反射调用       → getattr(DynamicFunctions(), "get_extract_data")("token") → "abc123"
```

- **不用正则**，用 `str.index()` + `str.count('${')` 循环定位，简单直观
- 输入是 dict 时先 `json.dumps` 转字符串，替换完 `json.loads` 还原类型
- 多个 `${...}` 占位符按出现次数循环处理，每次替换第一个

### 3.文件结构

| 文件 | 职责 |
|------|------|
| `common/functions.py` | `DynamicFunctions` 类，存放所有可被 YAML 调用的函数 |
| `base/client.py` | `replace_load()` 方法，解析 `${...}` 并反射调用 |

```python
# common/functions.py
class DynamicFunctions:
    def random_string(self, length=8):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(random.choice(chars) for _ in range(int(length)))

    def get_extract_data(self, key_path):
        return read_extract(key_path)
```

```python
# base/client.py — replace_load 核心
def replace_load(self, data):
    str_data = data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)
    for _ in range(str_data.count('${')):
        start = str_data.index('$')
        end = str_data.index('}', start)
        ref_all = str_data[start:end + 1]
        func_name = ref_all[2:ref_all.index('(')]
        func_params = ref_all[ref_all.index('(') + 1:ref_all.index(')')]
        result = getattr(DynamicFunctions(), func_name)(
            *func_params.split(',') if func_params else ""
        )
        str_data = str_data.replace(ref_all, str(result))
    return json.loads(str_data) if isinstance(data, dict) else str_data
```

> 注意：`replace_load` 的输入和输出类型永远一致——`str` 进 `str` 出，`dict` 进 `dict` 出。

## 6.common 和 base 的职责区别

| 目录 | 角色 | 特征 |
|------|------|------|
| `base/` | **执行引擎** | 知道"怎么跑"——串联请求、断言、提取的完整流程 |
| `common/` | **工具箱** | 只做"一件事"——读 YAML、算断言、生成随机值，互不依赖 |

- `base/client.py`（引擎）调用 `common/` 的各种工具完成一次测试
- `common/` 里的模块不依赖 `base/`，可以独立测试
- 打个比方：`base/` 是发动机，`common/` 是扳手和千斤顶

## 7.断言引擎

### 1.为什么从 client.py 抽出来

原来的断言直接写在 `call()` 里，用 `assert` 关键字——第一个断言失败就炸了，后面的不跑。另外断言逻辑和发请求逻辑混在一起，不好维护。

### 2.累加器模式

```python
# common/assertions.py
class AssertEngine:
    def run(self, validate_dict: dict, resp_dict: dict):
        failed = 0
        for key, expected in validate_dict.items():
            actual = deep_get(resp_dict, key)
            if not self._check(actual, expected):
                print(f"  [断言失败] {key}: 预期={expected}, 实际={actual}")
                failed += 1
            else:
                print(f"--[断言通过]--{key}")
        if failed > 0:
            raise AssertionError(f"{failed}/{len(validate_dict)} 条断言失败")
```

- 所有断言**全部跑完**再判断，不会中途停止
- `_check()` 支持三种判断：`"not_empty"`（非空）、`None`（为空）、等值比较
- `deep_get` 从 `client.py` 抽到 `common/deep_get.py`，assertions 和其他模块共用

## 8.关联提取机制（extract.yaml）

用来存放需要动态的提取响应体中的字段

### 1.数据流

```
测试启动 → conftest.py 清空 extract.yaml
    │
步骤1: 登录接口
    extract: {token: $.data.token}
    → 写入 extract.yaml
    │
步骤2: 获取用户信息
    header: Authorization: Bearer ${get_extract_data(token)}
    → replace_load 从 extract.yaml 读回注入
```

### 2.文件结构

| 文件 | 职责 |
|------|------|
| `common/yaml_utils.py` | YAML 读写基础工具：`read_yaml`、`append_yaml`（merge 模式）、`clear_yaml` |
| `base/extract.py` | extract 业务封装：`write_extract`、`read_extract`、`clear_extract` |
| `common/functions.py` | `get_extract_data(key)` — YAML 中 `${get_extract_data(token)}` 的桥接 |
| `conftest.py` | `clear_extract_yaml` fixture（session + autouse），每次运行前清空 |

### 3.append_yaml 的设计

如果采用用追加模式（`a` 模式）写 extract.yaml，同一个 key 可能重复出现，导致yaml文件读取崩溃。本项目改为 **merge 模式**：

```python
def append_yaml(file_path, new_data: dict):
    current = yaml.safe_load(f) or {}   # 读现有数据
    current.update(new_data)            # 同 key 覆盖
    yaml.safe_dump(current, f)          # 全量写回
```

> 同一个 key 永远只有最新值，不会有遗留，
> 代价是每次写入都需要全量读写，extract.yaml 大了会慢（虽然一般都很小）

## 9.业务场景模式

用于多接口串联，顺序执行

### 1.单接口 vs 业务场景

| | 单接口模式 | 业务场景模式 |
|---|---|---|
| YAML 结构 | 一个文件 = 一个接口 + 多个场景 | 一个文件 = 多个步骤（多接口按序执行）|
| 执行引擎 | `ApiClient.call()` — 一次调用一个请求 | `ProcessRunner.run()` — 串行执行多个步骤 |
| token 来源 | `auth_header` fixture 统一提供 | 流程第一步登录后 extract，后续步骤通过 `${...}` 读取 |
| 参数化 | `@parametrize` 拆成 N 个独立测试 | 多步骤作为一个整体，顺序执行 |

### 2.业务场景 YAML 格式

```yaml
# 顶层是列表，每个元素是一个步骤（一个接口）
- step_name: 用户登录
  request:                           # 步骤级配置（公共 header）
    method: post
    url: /users/login
    header:
      Content-Type: application/json
  cases:
    - case_name: 登陆成功
      json:
        username: testuser
        password: "123456"
      validate:
        code: 200
        data.token: not_empty
      extract:                       # 提取 token 供后续步骤使用
        token: data.token

- step_name: 获取个人信息
  request:
    method: get
    url: /users/me
  cases:
    - case_name: 成功获取用户个人信息
      header:                        # case 级 header（场景特化）
        Authorization: Bearer ${get_extract_data(token)}
      validate:
        code: 200
        data.username: testuser
    - case_name: 未登录被拒
      validate:                      # 不写 header = 不带 token
        code: 401
```

### 3.执行引擎 ProcessRunner

```python
# base/process.py
class ProcessRunner:
    def __init__(self, base_url):
        self.client = ApiClient(base_url)

    def run(self, steps: list):
        for step in steps:
            step_name = step['step_name']
            print(f"\n========步骤：{step_name} 开始执行========")
            for case in step['cases']:
                self.client.call(step['request'], case)
```

> `ProcessRunner` 不包含请求/断言/提取逻辑——全部复用 `ApiClient.call()`。它只负责**编排**：按步骤顺序遍历，把 `request` 和 `case` 喂给 `ApiClient`。

### 4.header 分层合并机制

一个请求的最终 header 由三层合并而来，从低到高优先级：

```
传入 headers（auth_header fixture）→ 步骤级 request.header → case 级 case.header
     低优先级                                            高优先级
```

```python
# base/client.py
merged_headers = {**headers, **base_headers, **case_headers}
```

- **步骤级** `request.header`：写 `Content-Type` 这种该接口所有场景都需要的公共头
- **case 级** `case.header`：写 `Authorization: Bearer ${get_extract_data(token)}` 这种场景特化的头
- **传入 headers**：供单接口测试的 `auth_header` fixture 快速注入 token

## 10.配置层、日志、Allure 报告

### 1.配置层（conf/）

把项目根目录、文件路径、API 地址这些"可能变、到处用"的东西集中管理：

| 文件 | 放什么 |
|------|--------|
| `conf/setting.py` | 路径常量（pathlib）、超时、日志级别 |
| `conf/config.ini` | 会变的东西：API base_api、数据库、报告类型 |
| `conf/config_reader.py` | 封装 `configparser`，暴露 `get(section, key)` |

```python
# conf/setting.py
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()

FILE_PATH = {
    'CONFIG': BASE_DIR / "conf" / "config.ini",
    'LOG': BASE_DIR / "logs",
    'EXTRACT': BASE_DIR / "extract.yaml",
    'REPORT_TEMP': BASE_DIR / "report" / "temp",
}

API_TIMEOUT = 30
```

```ini
# conf/config.ini
[api]
base_api = http://localhost:8080/api/v1
```

> `FILE_PATH` 字典是参考项目的经典设计——所有路径一个地方管，其他模块 `from conf.setting import FILE_PATH` 拿路径，永远不用手拼字符串。

### 2.日志模块（common/logger.py）

双 handler 输出：控制台只看 INFO 以上，文件存所有 DEBUG。按天滚动，文件名 `test.{YYYYMMDD}.log`。

```python
# common/logger.py
import logging
from datetime import datetime
from conf.setting import FILE_PATH

LOG_PATH = FILE_PATH['LOG']
LOG_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_PATH / f"test.{datetime.now():%Y%m%d}.log"

def get_logger(name: str = "apitest"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter('%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s')
    fh = logging.FileHandler(str(LOG_FILE), encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger

logger = get_logger()
```

> 防重复：`if logger.handlers` 确保 handler 不重复添加。模块级单例 `logger = get_logger()` 被其他模块直接 `from common.logger import logger` 使用。

### 3.Allure 报告集成

三个层次：

**运行层** — `run.py` 生成报告并注入环境信息：

```python
pytest.main(['-v', '--alluredir=./report/temp', '--clean-alluredir'])
shutil.copy('./environment.xml', './report/temp')  # 注入环境信息
os.system('allure generate ./report/temp -o ./report/html --clean')
os.system('allure open ./report/html')
```

**数据层** — `client.py` 在请求前后 attach 详情：

```python
allure.attach(f"{method} {url}", "请求接口", allure.attachment_type.TEXT)
allure.attach(str(merged_headers), "请求头", allure.attachment_type.TEXT)
allure.attach(resp.text, "响应体", allure.attachment_type.TEXT)
```

**标记层** — 测试文件加 Feature/Story 标签：

```python
@allure.feature("用户管理")
@allure.story("登录后获取个人信息")
def test_user_flow(set_base_url):
    ...
```

### 4.allure.step 分组

多步骤流程中，所有 `allure.attach` 平铺在 Test body 下分不清归属。用 `allure.step()` 嵌套分组：

```python
# process.py — 外层：步骤级
with allure.step(step_name):
    for case in step['cases']:
        self.client.call(...)

# client.py — 内层：用例级
with allure.step(case_name):
    # 请求、断言、提取逻辑
```

## 11. YAML 自动扫描 —— 告别手写 test.py

### 1.痛点

之前每新增一个接口，需要同时维护两个文件：

```
tests/test_users/
├── test_01.py    ← 手写（模板代码，每次复制改路径）
├── test_01.yaml  ← 手写（真正有价值的部分）
├── test_02.py    ← 又复制一份...
├── test_02.yaml
```

test.py 的内容几乎一模一样：读 YAML → `@parametrize` → `ApiClient.call()`。每加一个接口就复制粘贴一次，繁琐且容易出错。


### 2.方案：pytest_generate_tests hook

利用 pytest 的 `pytest_generate_tests` hook，在**收集测试阶段**自动扫描目录下所有 `.yaml` 文件，动态注入 `parametrize` 参数。test.py 永远只需写一次。

### 3.核心原理

```
pytest 启动
  ↓
发现 test_api.py → TestApi.test_single(..., api_config, case)  ← api_config/case 没有 fixture
  ↓
触发 pytest_generate_tests(metafunc)
  ↓                            ↓
rglob("*.yaml")           metafunc.parametrize('api_config,case', [...], ids=[...])
  ↓                            ↓
遍历所有 YAML，            把每一对 (api_config, case) 注入到 test_single，
按结构分类，拆成参数对       每一个 = 一个独立测试用例
  ↓
生成 4 个单接口 + 1 个流程 = 5 个测试用例
```

### 4.文件结构

| 文件 | 职责 |
|------|------|
| `tests/conftest.py` | 扫描器：`rglob("*.yaml")` → 分类（单接口/多流程）→ `metafunc.parametrize()` 注入 |
| `tests/test_api.py` | 骨架测试：只写一次，接收 `api_config` + `case`，调用执行引擎即可 |
| `tests/_template_single.yaml` | 单接口 YAML 模板 |
| `tests/_template_flow.yaml` | 多接口流程 YAML 模板 |

### 5.conftest.py 关键代码

```python
# tests/conftest.py
def pytest_generate_tests(metafunc):
    here = Path(__file__).parent
    single_params = []
    single_ids = []
    flow_params = []
    flow_ids = []

    for yf in sorted(here.rglob("*.yaml")):
        if yf.name.startswith("_"):
            continue                            # 跳过模板文件
        data = read_yaml(str(yf))

        if isinstance(data, list) and len(data) == 1 and 'cases' in data[0]:
            # 单接口：一个 request + 多个 cases
            api_config = data[0]['request']
            for case in data[0]['cases']:
                single_params.append((api_config, case))
                single_ids.append(case.get('case_name', '未命名'))

        elif isinstance(data, list) and len(data) > 1 and 'step_name' in data[0]:
            # 多接口流程：多个步骤
            flow_params.append(data)
            flow_ids.append(yf.stem)

    # 注入：只对声明了对应参数名的函数生效
    if 'api_config' in metafunc.fixturenames:
        metafunc.parametrize('api_config,case', single_params, ids=single_ids)
    if 'flow_data' in metafunc.fixturenames:
        metafunc.parametrize('flow_data', flow_params, ids=flow_ids)
```

### 6.骨架测试 test_api.py

```python
# tests/test_api.py
class TestApi:
    def test_single(self, set_base_url, auth_header, api_config, case):
        ApiClient(set_base_url).call(api_config, case, auth_header)

    def test_flow(self, set_base_url, flow_data):
        ProcessRunner(set_base_url).run(flow_data)
```

> 这两个函数**永远不用改**。新增接口时，只需要往目录下丢一个 YAML 文件。

### 7.pytest_generate_tests 的几个关键点

| 概念 | 说明 |
|------|------|
| `metafunc` | 元函数对象，代表 pytest 即将执行的测试函数 |
| `metafunc.fixturenames` | 测试函数需要哪些参数（list of str） |
| `metafunc.parametrize(name, values, ids)` | 注入参数化——和 `@pytest.mark.parametrize` 完全等价 |
| `ids` | 用例显示名，不传就用序号，传了就显示如 `test_single[成功登录用户]` |

> `pytest_generate_tests` 会在**每个测试函数**被收集时触发。所以用 `if 'api_config' in metafunc.fixturenames` 来区分要给哪个函数注入参数。

### 8.改造前后对比

| | 改之前 | 改之后 |
|----|--------|--------|
| 新增接口步骤 | 写 YAML + 手写 test.py | 只写 YAML |
| test.py 数量 | N 个（每个接口一个） | 1 个（永远不改） |
| YAML 和 test.py 的关联 | 硬编码文件路径 | 自动发现、自动注入 |
| 扩展新模块 | 新目录 + 新 test.py + conftest | 新目录 + 丢 YAML 即可 |

### 9.为什么 pytest 社区没有现成插件

pytest 插件列表中有 `pytest-yaml`，但它只是一个 `yaml_content` fixture，功能极其有限——需要手动指定 `--yaml-file`，不会自动扫描目录，也不支持参数化。

原因在于：每个人的 YAML 结构都不同（你的用 `request/cases`，参考项目用 `baseInfo/testCase`，别人的可能用 `steps/asserts`）。pytest 社区没法做一个"通用 YAML 自动化插件"来适配所有人。

`pytest_generate_tests` 正是为这种"太定制化、没有通用方案"的场景设计的。

### 10.扩展：模板文件机制

```python
if yf.name.startswith("_"):
    continue
```

下划线开头的 YAML 文件被跳过，用作模板。新增接口时复制模板 → 改字段 → 完成，降低上手门槛。


