# 请求校验

版本见[版本基线](version-baseline.md)。`validate.Validator()` 先调用请求的 `Validate() error`，再按顺序执行传入的 `ValidatorFunc`，第一次失败即返回 reason 为 `VALIDATOR` 的 Bad Request 并保留 cause。流式逐消息校验按[接收时机](streaming-patterns.md)接入，不能默认沿用 unary 的执行位置。

v3 不要求固定一种生成器。保留项目已有的 PGV、Protovalidate 或手写校验方案；修改校验引擎时核对错误正文、字段 presence、空集合与未知字段语义。

## 接入方式

- 已生成 `Validate() error`：直接使用 `validate.Validator()`。
- 自定义规则：传入 `func(value any) error`，只处理适用请求类型；规则应无副作用且并发安全。
- Protovalidate：使用项目固定的 `buf.build/go/protovalidate`，在回调里断言 `proto.Message` 后调用其验证 API。Buf lint/breaking 检查不能替代运行时校验。
- 规则 Proto 依赖、Buf lock、生成命令和 Go 运行库应一起维护，不能只复制 annotation 而没有对应执行器。

## 校验与授权

长度、格式和消息形状可在传输边界完成。数据库存在性、额度、金额不变量、权限与并发状态由业务执行，并在需要时于事务中重验。格式合法不等于允许执行业务。

校验错误可能包含字段内容，公开响应与日志都需遵守项目脱敏规则。验证无效输入确实阻止 handler 执行，并保留已有错误身份和调用方处理。

来源：[官方 Validate](https://go-kratos.dev/zh-cn/docs/component/middleware/validate/)、[v3 实现](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/validate/validate.go)、[Protovalidate](https://github.com/bufbuild/protovalidate-go)。
