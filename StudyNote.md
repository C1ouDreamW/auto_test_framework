## 1.获取api模型数据

`datamodel-code-generator` 是一个格式转换器，把 JSON Schema / OpenAPI / GraphQL schema 转成 Python 数据模型代码。

在测试方向，我们可以用它来帮我们把 API 的数据结构转换成 Python 的数据模型类，这样在测试中就可以直接使用这些类来进行数据验证和操作。

安装： 
```bash
pip install datamodel-code-generator
```

使用：
库默认支持 JSON Schema、OpenAPI、GraphQL schema 等格式的转换。使用时可以指定输入文件和输出文件，例如：

```bash
datamodel-codegen --input openapi.json --output model.py
```

若指定的文件为http/https的url，则需要额外安装 `httpx` 库：
```bash
pip install httpx # 这是一个 HTTP 客户端库
```