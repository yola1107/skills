# Panic 恢复

版本见[版本基线](version-baseline.md)。`recovery.Recovery()` 将其包裹的 handler panic 转为错误；可通过 `WithLogger(*slog.Logger)` 配置日志，通过 `WithHandler` 定义错误转换。

自定义 handler 的签名为 `func(context.Context, any, any) error`，最后一个参数是 panic 值。应返回稳定且不泄露实现细节的协议错误；默认请求日志及其脱敏边界见[请求日志](logging-patterns.md#请求日志与脱敏)。

## 覆盖边界

- Recovery 只覆盖当前调用栈，不覆盖新 goroutine、应用装配或没有进入该链的原生 HTTP handler。
- 构造失败优先返回 error 并清理部分资源。后台工作由生命周期 owner 管理取消、等待及失败策略。
- 数据库事务和其他资源仍用各自的 defer/cleanup，Recovery 不负责回滚或释放锁。
- 完成回调必须执行时，检查 panic 是否会跳过回调；固定并发 limiter 的正确组合见[限流](ratelimit-patterns.md)。

用业务错误处理预期失败。需要验证恢复时，触发明确的 handler panic，检查对外错误、脱敏日志及资源可再次使用；不能只断言进程没有退出。

来源：[官方 Recovery](https://go-kratos.dev/zh-cn/docs/component/middleware/recovery/)、[v3 实现](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/recovery/recovery.go)。
