# API 与生成

版本与模块路径见[版本基线](version-baseline.md)。先确定任务是新增协议还是兼容既有协议，再决定是否使用生成 HTTP 绑定。

## Proto 契约

- package、服务名、方法名、字段号、JSON 名称和空值语义都可能属于外部契约。
- 删除字段后保留其号码与名称，避免重用；`go_package` 应指向项目 module 下的实际 API 目录。
- 金额、时间、分页、幂等键与错误语义由业务契约决定，不能为套模板改成另一种表示。
- HTTP 绑定可以使用 `google.api.http` 的路径、query 和 body；复杂原生协议、签名原文或特殊响应也可使用[手写路由](transport-patterns.md)。

## 生成与注册

1. 沿用项目生成入口，工具准备与版本核对见 [CLI](cli-guide.md)。使用 HTTP annotation 时确保 googleapis proto 依赖可解析。
2. 核对 Kratos HTTP/error 生成器为独立 `/v3` 命令模块；固定实际可用版本。Protobuf 和 gRPC 的 Go 生成器仍使用它们自己的模块路径。
3. 生成后分别在 HTTP/gRPC server 注册需要的服务。只提供 gRPC 的接口无需额外 HTTP annotation。
4. 检查生成差异中的协议标识、JSON 行为、错误映射和 streaming 方法；同步真实调用方，再运行相应验证。

生成服务 stub 仅适合尚未实现的目标文件；已有 service 应在原实现中增加行为，避免覆盖。相关说明见 [CLI](cli-guide.md)、[编码](encoding-patterns.md)和[校验](validate-patterns.md)。

来源：[API 定义与生成](https://go-kratos.dev/zh-cn/docs/component/api/)。
