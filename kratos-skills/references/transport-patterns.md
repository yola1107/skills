# HTTP 与 gRPC

版本见[版本基线](version-baseline.md)。传输构建归 server，协议处理归 service；应用统一持有启动、停止和资源关闭责任。

## 服务构造

地址、超时和日志配置来自装配层，生成注册函数由实际 API 决定。健康检查须区分 handler 可响应与依赖、业务已就绪；readiness 按项目要求实现。构造示例见文末官方 HTTP/gRPC 文档。

## 手写路由与过滤器

`Server.Route` 注册接收 `http.Context` 的路由；`Handle`、`HandleFunc` 可接入原生 `net/http` handler。原生 handler 不会自动变成生成 RPC 中间件链，认证、operation、body 限制及错误编码要在实际入口明确接入。

生成 handler 会设置规范 RPC operation 并执行对应中间件。手写 `Router` handler 需要时显式设置 operation 并通过 `ctx.Middleware(...)` 调用业务；不能仅注册路由就假定 JWT 或限流已生效。原生 HTTP filter 通过 `http.Filter` 包住路由，适合 CORS、HTTP 请求限制和响应 header。

## 客户端入口与 TLS

HTTP 客户端使用 `http.NewClient`，gRPC 客户端使用 `grpc.NewClient(ctx, ...)`。基线与核对主干均无 Kratos `grpc.Dial`、`grpc.DialInsecure`；gRPC 未配置 `WithTLSConfig` 时默认使用明文凭据。TLS 按项目要求配置 CA 与 server name，保留证书验证；构造成功不代表目标业务已就绪。

HTTP 生成客户端和 `Client.Invoke` 执行 `WithMiddleware` 配置的链；`Client.Do` 直接进入底层请求路径，绕过该链。原生协议需要 `Do` 时，在实际调用边界或 RoundTripper 显式接入所需认证、metadata 与观测，并由调用方关闭响应 Body。验收实际发出的 header 与请求，不能只检查客户端构造选项。

`Do` 仍执行 ErrorDecoder，默认会读取并关闭非 2xx 响应 Body，再转换为框架错误。需要保留原始错误响应的转发入口，通过 `WithErrorDecoder` 明确处理策略，并验证 status、header、body 与关闭责任。

HTTP `WithTLSConfig` 只配置类型为 `*net/http.Transport` 的传输。若使用 OAuth2 等 RoundTripper 包装器，TLS 应配置在其底层 Transport；框架选项不会穿透任意包装器。

服务发现端点与 `WithDiscovery` 一起配置，见[注册发现](registry-patterns.md)。业务超时不能证明下游写入未提交；重试由幂等与业务结果决定。

## 连接与资源归属

沿用调用链 Context，按调用类型设置超时并复用连接。gRPC 连接由创建方调用 `Close()`；HTTP `Client.Close()` 在基线与核对主干中只关闭发现 resolver，不调用底层 Transport 的 `CloseIdleConnections()`。

持有独立 HTTP Transport 的装配点先取消并等待活动请求，再按需关闭空闲连接；共享 Transport 由其共同 owner 管理。关闭空闲连接不终止活动请求。流式 RPC 的取消、半关闭与中间件另见[流式调用](streaming-patterns.md)。

来源：[HTTP](https://go-kratos.dev/zh-cn/docs/component/transport/http/)、[gRPC](https://go-kratos.dev/zh-cn/docs/component/transport/grpc/)、[基线 HTTP 客户端](https://github.com/go-kratos/kratos/blob/v3.0.0/transport/http/client.go)、[基线 gRPC 客户端](https://github.com/go-kratos/kratos/blob/v3.0.0/transport/grpc/client.go)。
