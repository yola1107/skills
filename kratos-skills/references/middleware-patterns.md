# 中间件与 operation

版本见[版本基线](version-baseline.md)。Kratos 中间件处理 `context.Context` 和传入的消息对象；unary 通常在请求解码后执行，流式调用的执行时机另见[流式调用](streaming-patterns.md)。原生 HTTP filter 处理 `net/http`，作用位置不同。

## 顺序与覆盖

`middleware.Chain(a, b, c)` 形成 `a(b(c(handler)))`。按实际职责安排顺序：认证失败也需要观察时，观察逻辑放在认证外层；昂贵工作之前执行相应限流；Recovery 覆盖需要恢复的调用范围。校验与授权不能因链路顺序而泄露未授权数据。

资源释放使用 defer；需要完成回调的限流器还需关注 panic 路径，见[限流](ratelimit-patterns.md)。请求中间件不覆盖另起的 goroutine 或构造函数。

HTTP 生成或显式接入的 handler 使用 `http.Middleware`；gRPC 的 `grpc.Middleware`、`WithMiddleware` 只覆盖 unary。手写 HTTP handler 和客户端 `Do` 的接入边界见 [Transport](transport-patterns.md)，gRPC stream 的独立选项与限制见[流式调用](streaming-patterns.md)。

## operation selector

`middleware/selector` 选择哪些 RPC operation 使用一组中间件；它与负载均衡的顶层 `selector` 包不同。

```go
package example

import (
	"context"

	"github.com/go-kratos/kratos/v3/middleware"
	"github.com/go-kratos/kratos/v3/middleware/selector"
)

func ProtectedOperations(auth middleware.Middleware) middleware.Middleware {
	return selector.Server(auth).Match(func(_ context.Context, operation string) bool {
		return operation != "/example.user.v1.UserService/Login"
	}).Build()
}
```

示例在实际进入这条链的调用中仅豁免一个明确公开的 RPC；selector 不会自动覆盖其他传输入口。operation 来自传输绑定，不是 HTTP URL；新增公开方法应明确加入允许范围并覆盖验收。自定义中间件传递收到的 Context，修改上下文后把新 Context 交给 next。

内置 recovery、logging、validate、ratelimit、circuitbreaker 按需组合；JWT、OTel 的独立模块见版本基线。框架中间件不替代事务中的授权、幂等或业务状态重验。

来源：[中间件](https://go-kratos.dev/zh-cn/docs/component/middleware/overview/)、[v3 selector 实现](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/selector/selector.go)。
