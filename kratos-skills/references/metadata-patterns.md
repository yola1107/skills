# 请求元数据

版本见[版本基线](version-baseline.md)。数据结构使用核心 `metadata` 包，传输中间件位于核心 `middleware/metadata`；必要时用别名区分。

## Context API

- `metadata.FromServerContext(ctx)` 读取服务端元数据，检查是否存在。
- `metadata.AppendToClientContext(ctx, key, value, ...)` 返回新的客户端 Context；同名 key 使用 Set 覆盖，键值数量必须成对，并将返回的新 Context 传给下游。
- `NewServerContext`、`NewClientContext` 可显式设置元数据；共享 map/slice 需注意修改权，必要时使用 Clone。

传输层存在 header 不代表业务已信任其值。租户、玩家、角色和资金授权来自已认证身份及业务重验，不从任意客户端 metadata 直接赋予。

## 传播边界

服务端 `metadata.Server` 默认接收 `x-md-` 前缀，`WithPropagatedPrefix` 替换该接收范围。客户端 `metadata.Client` 的发送来源如下：

| 来源 | 是否受客户端前缀过滤 |
| --- | --- |
| `WithConstants` | 否 |
| 显式 client Context metadata | 否 |
| 从 server Context 自动转发的 metadata | 是，默认仅 `x-md-global-` |

客户端 `WithPropagatedPrefix` 只改变最后一行，不能作为所有出站 header 的白名单。完整允许范围在写入各来源及传输边界落实；gRPC 流的建流 header 注入另见[流式调用](streaming-patterns.md)。

只传播当前下游需要的非敏感元数据。检查跨服务和跨信任域时的允许范围，不把外部 header 全量复制到内部调用。Trace Context 按项目 OTel propagator 管理；不要同时维护相互冲突的私有 trace 格式。

来源：[官方 metadata](https://go-kratos.dev/zh-cn/docs/component/metadata/)、[v3 元数据中间件](https://github.com/go-kratos/kratos/blob/v3.0.0/middleware/metadata/metadata.go)。
