# slog 日志

版本见[版本基线](version-baseline.md)。v3 应用、日志中间件和 Recovery 使用 `*slog.Logger`，无需旧式 Logger/Helper 适配器。

装配点通过 `slog.Handler` 构造 logger，传给 `kratos.Logger(logger)`、`logging.Server(logger)` 或 `logging.Client(logger)`。请求日志使用 `InfoContext` 等方法，携带已有 Context；是否允许业务层直接依赖日志由项目架构决定，不强制给每个 Usecase 注入 logger。

## 字段、适配与退出

- 使用稳定业务键、operation 和必要诊断；禁止输出令牌、密钥、完整签名正文或私密玩家数据。
- 通过 `slog.Handler`、`HandlerOptions.ReplaceAttr` 或经核对的 Kratos 过滤能力处理实际输出的属性。异步 handler 必须有容量与停止/flush 责任。
- 日志库集成以 slog handler 为边界；trace 属性需要由项目的 handler/OTel 集成提取，传入 Context 不保证自动打印 trace ID。
- 错误在负责处理的边界按需记录，避免逐层重复；日志是观察证据，不替代业务持久状态。

## 请求日志与脱敏

基线 logging 中间件把请求格式化成 `args` 字符串；优先调用请求的 `logging.Redacter.Redact() string`，否则使用 `String()` 或格式化表示。仅过滤名为 `password`、`token` 的 slog 属性，不能清理已经嵌在 `args` 中的值。按实际请求类型提供安全的 Redact，或在 handler 中删除/替换整个 `args`；生成消息的适配遵守项目生成约定。

Recovery 在调用自定义错误 handler 之前记录 `panic`、完整 `request` 和 `stack`，不会调用 logging 的 Redacter。其 logger/handler 需单独处理这些属性；只更换 `WithHandler` 不能改变此前的日志。嵌在任意对象或字符串中的字段也不会因同名属性过滤而自动脱敏。

修改这些链路时，用含敏感标记的合成请求检查正常、错误和 panic 的实际输出，同时保留项目需要的诊断信息。

来源：[v3 日志文档](https://go-kratos.dev/zh-cn/docs/component/log/)、[基线 logging](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/logging/logging.go)、[基线 Recovery](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/recovery/recovery.go)、[标准库 slog](https://pkg.go.dev/log/slog)。
