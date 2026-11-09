# OpenAPI

Kratos 版本见[版本基线](version-baseline.md)。OpenAPI 生成器是独立工具，选择项目已有的实现与固定版本；核心 v3 不会自动选择 OpenAPI 工具版本。

## 生成流程

1. 先确定使用的 OpenAPI 格式版本、生成器和已有配置，避免把不同生成器的 option 混用。
2. Proto 中 HTTP annotation、请求/响应 schema、错误、认证和分页与实际接口保持一致；导入文件需在 Buf/protoc 依赖中可解析。
3. 使用项目固定的 Makefile/Buf 命令生成，检查生成差异和对外契约。新的文档生成配置不能改变业务路由。
4. 手写路由按实际行为补充描述；生成器不会自动理解任意 net/http handler。

## 提供文档

静态文档或 Swagger UI 按项目已有入口发布。是否公开、鉴权方式与版本由任务要求决定；不要为了生成文档默认增加公共管理端点或引入另一套服务。

核对金额/int64 的 JSON 形态、null/空集合、错误正文和认证 header。文档声明 JWT bearer 不会自动安装认证中间件；客户端生成结果也需与实际协议样本比对。

来源：[官方 OpenAPI 指南](https://go-kratos.dev/zh-cn/docs/guide/openapi/)。
