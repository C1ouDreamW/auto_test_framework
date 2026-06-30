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
[待定]

### 2.pytest的parametrize标记

对于上面说的YAML文件，一个接口可能包含多个case，如果一个一个地写函数会变得重复且繁琐。

parametrize是pytest提供的一个标记，用于生成多个测试用例。它可以接受一个列表或元组作为参数，每个元素都会生成一个独立的测试用例。

我们可以在测试用例中读取YAML文件，然后使用parametrize标记来生成多个测试用例。

parametrize一般接受两个参数：
1. 参数名：一个字符串，表示测试函数的参数名，可以是多个参数名，用逗号分隔
2. 参数值：一个列表或元组，表示测试函数的参数值，每个元素都会生成一个独立的测试用例。

使用方法：
```python 
@pytest.mark.parametrize("case", cases)
def test_login(case): # 记得传入定义的参数名
```