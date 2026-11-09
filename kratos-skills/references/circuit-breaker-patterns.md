# 客户端熔断

版本见[版本基线](version-baseline.md)。v3 核心在客户端提供 `circuitbreaker.Client()`，默认按 RPC operation 管理独立熔断器。服务端过载保护使用合适的限流或并发控制，见[限流](ratelimit-patterns.md)。

## 实际 API

自定义熔断器实现 `Allow() error`、`MarkSuccess()`、`MarkFailed()`，通过 `circuitbreaker.Client(circuitbreaker.WithBreakerFactory(factory))` 注入；工厂类型为 `func() circuitbreaker.CircuitBreaker`。

工厂为每个 operation 返回独立实例；实例自身必须并发安全。无需自定义时直接用 `circuitbreaker.Client()`。v3 核心已内置默认实现，不需要为了启用默认熔断器额外安装 Aegis。

核心选项是 `WithBreakerFactory`。不要根据其他库的命名猜测 `WithBreaker`、`WithFilter` 或服务端构造函数；核对锁定版本的导出 API。

## 失败分类与恢复

基线版本默认把 InternalServer、ServiceUnavailable 和 GatewayTimeout 计为失败，其他结果按核心实现处理。业务需要不同分类时先确认错误映射和业务契约，再设计相应适配，不假定有任意 error filter 选项。

熔断器决定是否允许调用，不提供交易补偿、幂等或安全重试。超时、熔断拒绝和远端已提交但未收到响应要分别处理；资金 UNKNOWN 不得被普通 fallback 成功值或“余额为零”替代。

观测 operation、失败分类、被拒绝请求和恢复效果。恢复探测方式由具体算法决定，不能把通用 CLOSED/OPEN/HALF-OPEN 图当作所有实现的精确状态机。

来源：[官方熔断文档](https://go-kratos.dev/zh-cn/docs/component/middleware/circuitbreaker/)、[锁定版本源码](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/circuitbreaker/circuitbreaker.go)。
