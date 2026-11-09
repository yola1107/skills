# 版本基线

本技能以 **Kratos v3.0.0**（`668db92c`）为稳定基线。2026-11-06 核对时，最新正式版仍为 v3.0.0；本地与远端 `main` 均为 **`dd0fb7df1e325daf5ffb9c30862be8f1091763eb`**，比正式版多 7 个提交。下文将该 commit 简称为“核对主干”，不代表项目已采用它。

未特别标明的核心行为适用于上述两个版本；主干新增能力和修复单独列出。实际依赖与工具链以项目 `go.mod`、生成和构建配置为准。

## 模块与 API

| 能力 | v3 路径或行为 |
| --- | --- |
| 核心 | `github.com/go-kratos/kratos/v3` |
| 日志 | 标准库 `log/slog`；应用及日志中间件接收 `*slog.Logger` |
| HTTP/gRPC 客户端 | 核心 `transport/http.NewClient`、`transport/grpc.NewClient` |
| 配置 | 核心的 `config`、`config/file`、`config/env` |
| JSON | `encoding/json` 为普通 Go JSON；`encoding/protojson` 为 protobuf JSON |
| JWT | `github.com/go-kratos/kratos/contrib/middleware/jwt/v3` |
| OTel | `github.com/go-kratos/kratos/contrib/otel/v3`，按需导入 `metrics`、`tracing`、`log` |
| 注册发现、远程配置 | 相应 contrib provider 的 `/v3` 模块；按所选 provider 核对依赖与 API |
| 熔断 | 核心 `middleware/circuitbreaker`；自定义注入用 `WithBreakerFactory` |
| 限流 | 核心 `middleware/ratelimit`；`Limiter.Allow() (DoneFunc, error)` |
| 校验 | 核心 `middleware/validate`；支持 `Validate() error` 与 `ValidatorFunc` |
| HTTP 路径与绑定 | `http.BuildPath`、`http.Context.Bind/BindQuery/BindVars/BindForm` |

contrib、CLI、生成器均可能是独立 module，不能因为核心是 v3.0.0 就假定其 tag 相同。读取各 module 的 `go.mod`，使用已核实的固定版本；第三方库保留自身主版本，例如 JWT 库的 `/v5`。

## 正式版与主干差异

| 范围 | v3.0.0 | 核对主干 |
| --- | --- | --- |
| [默认配置解析](config-patterns.md) | 布尔占位符保持字符串，扫描到 bool 字段可能失败 | 完整占位符解析出的 `true`/`false` 转为 bool |
| [BuildPath](encoding-patterns.md#路径与表单) | 路径值直接替换，Proto 字段名解析不完整 | 按路径模板转义，支持 Proto/JSON 字段名 |
| [Form FieldMask](encoding-patterns.md#路径与表单) | 编码可能修改输入的 `Paths` | 保留输入对象 |
| [Form Timestamp](encoding-patterns.md#路径与表单) | 使用本地时区后添加 `Z`，非 UTC 环境会产生时间偏移 | 使用 UTC 编码 |
| [OAuth2](oauth2-patterns.md) | 仓库中尚无该 module | 新增独立 OAuth2 中间件 module |

配置修复来自 [`05dff1ae`](https://github.com/go-kratos/kratos/commit/05dff1ae)，路径与表单修复来自 [`3f6b3b6c`](https://github.com/go-kratos/kratos/commit/3f6b3b6c)，OAuth2 来自 [`c8c129b5`](https://github.com/go-kratos/kratos/commit/c8c129b5)。采用其他版本时核对相关实现，不把主干修复视为正式版已有行为。

## 工具链兼容

核心声明的最低 Go 版本为 1.25；最低版本约束不等于所有后续工具链与依赖组合都已验证。已复现 Go 1.27.3 配合上游 `x/net v0.54.0` 时，gRPC 编译报 `undefined: http2.TrailerPrefix`：该符号在对应的 Go 1.27 构建分支不可用。

隔离对照中改用 `x/net v0.55.0`，并由依赖选择更新到 `x/sys v0.45.0` 后，相关核心与 OAuth2 测试通过。这是特定组合的兼容证据；项目沿用自己的已验证依赖，出现同类错误时核对实际选中的版本和 build tag，按授权处理依赖变更。

## 涉及版本或 API 差异时

- 保持项目锁定版本；旧主版本只说明本次涉及的不兼容点，依赖升级须在授权范围内。
- 涉及生成或迁移时，核对相关工具声明、Buf/Makefile、生成产物和 Kratos 路径，避免混入旧主版本。
- 旧日志 Helper、核心 JWT/OTel 中间件、旧 HTTP binding 包和 Aegis 选项需要按功能迁移，不能仅替换 import 后缀。
- codec 迁移按[编码契约](encoding-patterns.md)核对，保留冻结原文与签名正文。
- 仅核对本次使用且尚未确认的 API；依赖或工具版本变化后重核受影响部分。官方文档用于查用法，准确签名和行为以项目锁定的 module 源码为准，源码引用使用对应 tag/commit；浮动 `main` 只用于导航。

## 来源

- [核心 v3.0.0 源码](https://github.com/go-kratos/kratos/tree/v3.0.0)
- [核对主干源码](https://github.com/go-kratos/kratos/tree/dd0fb7df1e325daf5ffb9c30862be8f1091763eb)
- [官方迁移说明](https://go-kratos.dev/zh-cn/docs/migration/v2-to-v3/)
- [独立 contrib 模块](https://go-kratos.dev/zh-cn/docs/getting-started/plugin/)

本文记录 API 核对基线；各项目的数据库、注册中心、鉴权和遥测集成仍需在其允许环境验收。
