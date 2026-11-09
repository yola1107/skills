# 流式调用

用于 gRPC stream 与生成的 HTTP SSE/WebSocket 绑定。以下核心行为已核对[稳定基线与主干](version-baseline.md)；生成器按项目独立版本核对。既有原生 WebSocket 协议继续遵守原契约。

## gRPC 中间件边界

流式选项为服务端 `grpc.StreamMiddleware` 和客户端 `grpc.WithStreamMiddleware`。基线在 `SendMsg`、`RecvMsg` 时执行这些链，不包住整个业务流生命周期：客户端流或双向流的业务方法可能先于链执行；传给 next 的派生 Context 也不会保存到 `stream.Context()`。

需要在业务方法前完成的鉴权，在 Kratos `grpc.StreamInterceptor` 选项中传入原生 stream interceptor，并包装原生 `grpc.ServerStream.Context()` 向业务传递可信身份。逐消息校验放在成功接收、解码之后；将 `validate.Validator()` 直接放入流式链，会在 Recv 解码前处理目标对象。Recovery、整条流的并发限制和计时也按其实际覆盖范围接入，不能把逐消息执行等同于包裹整个方法。

客户端在调用底层建流函数前设置原生 gRPC outgoing metadata，或使用经核对的 `PerRPCCredentials`。基线的 `WithStreamMiddleware(metadata.Client())` 在建流后执行，写入传输 header 的值不会自动进入建流请求。验证对端实际收到的凭据与 metadata。

gRPC unary timeout 不自动施加到流上；流的调用方持有取消与截止时间。`CloseSend()` 表示发送结束，仍需完成接收或取消整条流；连接级 `Close()` 会影响该连接上的所有流。

## HTTP 绑定与鉴权

| RPC 类型 | 生成 HTTP 传输 | 路由方法 |
| --- | --- | --- |
| 服务端流 | SSE | 保留 HTTP annotation 的方法 |
| 客户端流、双向流 | WebSocket | 用 GET 完成 upgrade，即使 annotation 写的是 POST |

生成的 HTTP middleware 包裹 service 方法；WebSocket upgrade 发生在这条链之前。要求在握手阶段以 HTTP 401/403 拒绝时，在 HTTP filter 或前置路由完成鉴权。客户端流和双向流还需在每次成功 Recv 后校验消息，初始中间件调用没有已解码的请求消息。

## HTTP 流退出

服务端流的 Context 只保留 value，剥离请求的取消和 deadline；`SetContext` 同样执行这种剥离。给它传入 `WithCancel` 或 `WithTimeout`，不会让 `stream.Context().Done()` 成为退出信号。

服务端业务等待使用另行持有的生命周期 Context；阻塞 I/O 在开始读写前设置 `SetReadDeadline`、`SetWriteDeadline`，退出时关闭流并等待相关工作结束。处理 Send/Recv 错误和 EOF；SSE 缓冲、WebSocket upgrade 与代理 idle timeout 按实际链路验证。

客户端 SSE 可通过取消请求 Context 或 `CloseSend()` 关闭响应 Body。基线 WebSocket 客户端则只在握手时使用 Context 取消，建立连接后的 Recv 不监听 Done，`CloseSend()` 也仅发送结束帧。其公共 ClientStream 接口没有连接级 Close/deadline 方法；需要可靠取消时，使用能控制底层连接的适配实现关闭与等待，或在获准的版本变更中核实该限制已解决。只设置 Context 超时或另起 goroutine 放弃等待，不能证明连接和 Recv 已退出。

涉及流式变更时，覆盖未认证调用进入业务前被拒绝、对端收到预期 header、无效消息被拒绝、取消和停止能结束等待，以及半关闭/EOF。重连、恢复位置和投递保证由应用协议定义。

来源：[官方 HTTP 流式说明](https://go-kratos.dev/zh-cn/docs/component/transport/http-streaming/)、[基线 gRPC 服务端拦截器](https://github.com/go-kratos/kratos/blob/v3.0.0/transport/grpc/interceptor.go)、[基线 gRPC 客户端](https://github.com/go-kratos/kratos/blob/v3.0.0/transport/grpc/client.go)、[基线 HTTP stream](https://github.com/go-kratos/kratos/blob/v3.0.0/transport/http/stream.go)、[核对生成器模板](https://github.com/go-kratos/kratos/blob/dd0fb7df1e325daf5ffb9c30862be8f1091763eb/cmd/protoc-gen-go-http/httpTemplate.tpl)。
