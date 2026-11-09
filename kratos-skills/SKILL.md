---
name: kratos-skills
description: >-
  Kratos v3 开发与排错：HTTP/gRPC、分层与 Wire、配置与生命周期，以及框架中间件和 contrib 集成。
license: MIT
---

# Kratos v3

[中文官方文档](https://go-kratos.dev/zh-cn/docs/)解释框架用法；具体行为以项目锁定版本的源码为准，差异见[版本基线](references/version-baseline.md)。模板不决定项目的业务契约、目录或基础设施。

## 工作方式

1. 按任务读取适用的仓库约定、相关实现与下方专题，复用已读且未变化的资料。项目版本尚未确认时查 `go.mod`，涉及生成时查项目生成命令。
2. 核对本次使用且尚未确认的 API 与接入边界；优先查锁定依赖源码，本地资料不足时查官方文档与对应 tag。依赖或工具版本变化后重核相关部分。
3. 沿用现有应用目录、module、数据访问与生成工具。分层通常为 `service → biz ← data`，职责与资源归属见[架构与装配](references/architecture-patterns.md)；Ent、JWT、注册中心和遥测按需求选用。
4. 在项目允许的环境验证受影响行为及仓库规定的必需项；通过后仅因新增改动、失败或证据缺口补查。证据选择见[交付复核](best-practices/overview.md)。

## 任务与授权边界

- 用户明确要求优先于技能建议；分析、评审与规划默认只读。已授权实施应完成修改、调用方同步、必要生成与验证，无需重复确认；关键业务、兼容性或权限未决时，只暂停依赖该决定的部分并询问。
- 保留既有协议、金额与权限规则、事务隔离、锁序、幂等、提交未知及恢复证据；资源清理须覆盖取得后的失败与退出路径。原生协议可用手写 handler，生成绑定按契约选用。
- 依赖升级、新配置或表结构、协议变化及提交、推送、部署和外部环境操作均以任务授权为限。调用技能或采用示例不扩大授权。

## 按问题查阅

| 问题 | 参考 |
| --- | --- |
| 核对版本、核心与 contrib 模块 | [版本基线](references/version-baseline.md) |
| 应用分层、Repo/Usecase、Wire 与 cleanup | [架构与装配](references/architecture-patterns.md) |
| App hooks、停止预算与启动失败清理 | [应用生命周期](references/architecture-patterns.md#生命周期与失败清理) |
| Proto、生成流程、字段兼容 | [API](references/api-patterns.md) |
| HTTP/gRPC 服务、客户端与手写路由 | [Transport](references/transport-patterns.md) |
| gRPC 流、SSE/WebSocket、逐消息校验与流退出 | [流式调用](references/streaming-patterns.md) |
| JSON/protojson、错误正文与自定义 codec | [编码](references/encoding-patterns.md) |
| OpenAPI 生成与文档服务 | [OpenAPI](references/openapi-guide.md) |
| 业务错误、cause 与协议映射 | [错误](references/error-patterns.md) |
| 中间件顺序、operation selector | [中间件](references/middleware-patterns.md) |
| 配置加载、Watch 与资源替换 | [配置](references/config-patterns.md) |
| 注册、发现与连接生命周期 | [注册发现](references/registry-patterns.md) |
| 节点选择与负载均衡 | [Selector](references/selector-patterns.md) |
| 客户端熔断 | [Circuit breaker](references/circuit-breaker-patterns.md) |
| BBR、并发限制与完成回调 | [Rate limiter](references/ratelimit-patterns.md) |
| panic 恢复和后台任务 | [Recovery](references/recovery-patterns.md) |
| slog、脱敏与日志归属 | [日志](references/logging-patterns.md) |
| OpenTelemetry 指标 | [Metrics](references/metrics-patterns.md) |
| Trace provider、传播与退出 | [Tracing](references/tracing-patterns.md) |
| 请求元数据与可信身份 | [Metadata](references/metadata-patterns.md) |
| JWT contrib 与认证边界 | [认证](references/auth-patterns.md) |
| OAuth2 TokenSource、introspection 与 scope | [OAuth2](references/oauth2-patterns.md) |
| Validate 方法、Protovalidate 与业务校验 | [校验](references/validate-patterns.md) |
| 已使用 Ent 的项目 | [Ent](references/ent-patterns.md) |
| CLI 与生成工具 | [CLI](references/cli-guide.md) |
| 按改动选择验收证据 | [交付复核](best-practices/overview.md) |
| 生成、编译、运行问题 | [排错](troubleshooting/common-issues.md) |

安装或更新技能时查[使用说明](getting-started/claude-code-guide.md)。
