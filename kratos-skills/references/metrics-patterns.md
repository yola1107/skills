# OpenTelemetry 指标

版本见[版本基线](version-baseline.md)。v3 指标中间件位于 `github.com/go-kratos/kratos/contrib/otel/v3/metrics`，属于独立 module；根据项目固定版本核对其构造选项，不使用不存在的核心 metrics 中间件路径。

## 接入责任

1. 先明确需要观察的请求数量、错误、延迟或资源瓶颈，复用项目已有 meter/provider。
2. 装配层创建 provider、reader/exporter 及 instruments，按模块实际 API 创建 Server/Client 中间件。
3. 绑定 transport 并覆盖错误和取消路径。手写 HTTP handler 是否计量取决于实际链路。
4. 应用停止业务工作后，以有界 Context flush/shutdown provider；构造部分失败时也清理已取得资源。

Prometheus 导出需要相应 reader/exporter 和受控 scrape 入口；安装中间件不会自动暴露有效的指标端点。Exporter 和 SDK 使用各自固定版本。

## 维度与判断

标签使用稳定、有限集合，如 service、operation、结果类别。玩家 UID、交易号、完整 URL、任意错误字符串不作为指标标签。HTTP 路由优先用模板或规范 operation，避免每个 path 参数生成时序。

指标是聚合观察，不是资金成功或事务提交的权威证据。延迟分布、拒绝量和资源占用一起看；阈值依据本地测量与业务预算配置。

来源：[官方指标中间件](https://go-kratos.dev/zh-cn/docs/component/middleware/metrics/)。具体 contrib API 按项目锁定的独立 module 源码核对。
