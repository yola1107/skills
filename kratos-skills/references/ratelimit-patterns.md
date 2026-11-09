# 限流与并发限制

版本见[版本基线](version-baseline.md)。`ratelimit.Server()` 默认使用内置 BBR 限流器；自定义实现通过 `ratelimit.WithLimiter(limiter)` 传入。参数是 Option，不能直接把 limiter 传给 Server。

BBR、固定速率和最大并发解决不同问题。先确定要限制的资源、范围和拒绝响应；跨实例总额度需要共享权威，本机 limiter 不提供分布式保证。任务给出固定限额时直接使用该值，不自动新增配置项。

## 先选择接入边界

- 生成 RPC handler 或明确进入 Kratos middleware 的调用：使用下文的完成回调方案。默认拒绝会形成 Kratos `RATELIMIT` 错误，需确认错误编码满足现有契约。
- 原生 `Handle`/`HandleFunc`：不会执行 RPC middleware。固定并发用原生 HTTP filter 包装目标 handler，并复用既有协议的拒绝 writer。注册方法与 filter 位置见 [Transport](transport-patterns.md)。

以下原生入口示例不读取或改写请求；`reject` 由应用提供，负责协议规定的忙碌响应及必要签名：

```go
package example

import (
	"errors"
	"net/http"

	khttp "github.com/go-kratos/kratos/v3/transport/http"
)

func ConcurrencyFilter(limit int, reject http.Handler) (khttp.FilterFunc, error) {
	if limit <= 0 || reject == nil {
		return nil, errors.New("positive limit and rejection handler required")
	}
	slots := make(chan struct{}, limit)
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			select {
			case slots <- struct{}{}:
				defer func() { <-slots }()
				next.ServeHTTP(w, r)
			default:
				reject.ServeHTTP(w, r)
			}
		})
	}, nil
}
```

构造一次后用 `srv.Handle(path, filter(existingHandler))` 包装目标入口；除非所有路由都应共享额度，否则不用全局 filter。panic 展开时 defer 仍释放额度，panic 的对外处理沿用原生入口既有机制。此分支不需要额外实现 Kratos Limiter。

## 完成回调

接口是 `Allow() (ratelimit.DoneFunc, error)`，成功后请求完成必须调用返回的函数。以下是可独立编译的固定并发示例，不是 token bucket；队满立即拒绝，不等待：

```go
package example

import (
	"errors"
	"sync"

	"github.com/go-kratos/kratos/v3/middleware"
	"github.com/go-kratos/kratos/v3/middleware/ratelimit"
	"github.com/go-kratos/kratos/v3/middleware/recovery"
)

type concurrencyLimiter struct {
	slots chan struct{}
}

func NewConcurrencyLimiter(limit int) (ratelimit.Limiter, error) {
	if limit <= 0 {
		return nil, errors.New("concurrency limit must be positive")
	}
	return &concurrencyLimiter{slots: make(chan struct{}, limit)}, nil
}

func (l *concurrencyLimiter) Allow() (ratelimit.DoneFunc, error) {
	select {
	case l.slots <- struct{}{}:
		var once sync.Once
		return func(ratelimit.DoneInfo) {
			once.Do(func() { <-l.slots })
		}, nil
	default:
		return nil, ratelimit.ErrLimitExceed
	}
}

func Protect(limiter ratelimit.Limiter) middleware.Middleware {
	return middleware.Chain(
		ratelimit.Server(ratelimit.WithLimiter(limiter)),
		recovery.Recovery(),
	)
}
```

基线的 `ratelimit.Server` 在 handler 正常返回后调用 Done，而不是 defer 调用。上述组合把 Recovery 放在该限流器的内侧，让 handler panic 转成返回错误后仍释放额度；应用可按需要再设置外层 Recovery。仅有外层 Recovery 不能保证这个完成回调执行。

## 使用范围与验收

- 按 IP、用户或租户建 limiter 时，需要可信身份、并发安全和有界缓存/过期回收。任意请求键不能无限创建常驻实例。
- 固定速率可适配项目已有算法；适配层仍应满足完成回调协议。不要引用不存在的核心 `NewTokenBucket` API。
- 验证额度耗尽、释放后再用、重复 Done、并发请求和 handler panic；请求取消时由实际 handler 退出并完成释放。
- 原生签名入口验证实际注册路径受保护，请求 body、签名 header、path/query 保持原值，且满额时复用原协议响应；原生 filter 无 Done，验证其 defer 释放即可。
- 配置速率、窗口和容量要依据预算与测量，示例数值不构成生产建议。

来源：[官方限流文档](https://go-kratos.dev/zh-cn/docs/component/middleware/ratelimit/)、[v3 中间件实现](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/ratelimit/ratelimit.go)。
