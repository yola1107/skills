# 错误身份与协议映射

版本见[版本基线](version-baseline.md)。业务错误归业务 owner，底层诊断作为 cause 保留；service/transport 决定调用方可见的协议错误。

## v3 错误 API

Kratos 错误包可用 `kerrors` 与标准库区分。`code`、`reason`、`message`、`metadata` 面向协议；`WithCause` 保留内部原因。用标准库 `errors.Is/As` 检查原因，用 Kratos `errors.FromError` 或生成的错误 helper 检查协议错误；不要通过错误字符串匹配业务状态。

## 映射边界

- 区分缺行、冲突、取消、超时、连接故障和提交结果未知；查询失败不能当成不存在后继续写入。
- 保持既有 gRPC status 与 HTTP 正文契约。Kratos 默认编码只是可选实现，不能强制把所有接口改成统一 errors.proto。
- `code` 与 gRPC status 不是可直接互换的整数；通过框架转换或现有映射处理。
- 对调用方隐藏 SQL、DSN、凭据和堆栈；内部 cause 可由负责处理的边界记录。
- RPC 或 COMMIT 超时不能推断回滚成功；UNKNOWN、重试资格和已持久事实须保留。

需要生成错误 helper 时，在协议目录定义错误枚举，用项目固定的 v3 error 生成器产生代码；沿用现有错误方案时无需为采用框架而迁移。

来源：[官方错误文档](https://go-kratos.dev/zh-cn/docs/component/errors/)、[v3 错误实现](https://github.com/go-kratos/kratos/blob/v3.0.0/errors/errors.go)。
