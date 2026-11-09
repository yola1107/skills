# 分布式追踪

版本见[版本基线](version-baseline.md)。v3 追踪中间件使用 `github.com/go-kratos/kratos/contrib/otel/v3/tracing`；provider、exporter、resource、sampling 和 shutdown 由应用明确管理。

## 生命周期与传播

- 复用项目已有 OTel 初始化，避免重复设置全局 provider 或 propagator。
- 按模块版本创建 Server/Client 中间件，并配置一致的传播格式。服务端提取与客户端注入都要实际接入，单侧启用不能形成完整链路。
- 下游调用沿用请求 Context；手动 span 使用收到的 Context 创建，结束时调用 End，必要时记录已脱敏错误。
- 停止请求与后台工作后执行有界 flush/shutdown；退出时直接取消用于收尾的 Context 可能丢失待发送数据。

OTLP、Jaeger、Zipkin 等 exporter 是可选独立依赖。按项目现有后端选择，核对协议与 endpoint；本技能不默认安装某个后端或连接外部测试环境。

## 采样与业务语义

使用明确的采样与数据预算，span 属性保持低敏感性。调用成功、网络超时、取消和提交未知应保留原有业务区别；trace 不作为持久幂等或资金事实。

业务关键跨度可覆盖事务、下游等待和恢复，但不要逐条 SQL/字段机械加 span。异步工作需要明确的父子/关联语义与自己的生命周期，不能无限继承已结束请求的资源。

来源：[官方 tracing](https://go-kratos.dev/zh-cn/docs/component/middleware/tracing/)。具体 contrib API 按项目锁定的独立 module 源码核对。
