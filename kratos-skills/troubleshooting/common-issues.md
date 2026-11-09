# 排错入口

保留最小失败命令、原始错误及已有改动，按症状核对直接调用路径。涉及 module、API 或工具版本差异时查[版本基线](../references/version-baseline.md)，复用未变化的核验结果。

| 症状 | 优先核对 |
| --- | --- |
| import/符号不存在 | go.mod、实际 module 源码与工具版本；v3 slog、JWT/OTel 独立路径、熔断工厂和限流完成回调 |
| Go 1.27 编译报 `http2.TrailerPrefix` 不存在 | 实际选中的 x/net 与构建分支，见[工具链兼容](../references/version-baseline.md#工具链兼容) |
| Wire 无法提供类型 | 构造返回类型、ProviderSet、接口绑定、injector 参数和 build tag；保持 wire import |
| 生成代码与 service 不匹配 | Proto 来源、生成器路径、固定版本和生成范围；修改输入后重生成 |
| HTTP 返回格式变化 | json/protojson、Content-Type/Accept、decoder/encoder 与旧样本 |
| HTTP 路由绕过认证或限流 | 原生 handler/Router 是否显式进入 middleware，operation 是否设置，selector 是否误豁免 |
| 客户端凭据或 metadata 未到达对端 | HTTP Invoke/Do 的[入口差异](../references/transport-patterns.md#客户端入口与-tls)、[流式建流](../references/streaming-patterns.md)与实际 header |
| 流式鉴权、校验或退出不生效 | [逐消息执行、Context 与关闭边界](../references/streaming-patterns.md) |
| 已配置脱敏但日志仍含请求秘密 | logging 的 args 与 Recovery 的 request/panic，见[请求日志](../references/logging-patterns.md#请求日志与脱敏) |
| JWT 校验失败 | contrib 版本、JWT 类型、算法、key function、claims、issuer/audience/时钟与公开 operation |
| OAuth2 token 或 scope 失败 | [OAuth2](../references/oauth2-patterns.md) 的 Validator、策略、链顺序、TokenSource 超时与缓存 |
| 请求永远被限流 | 完成回调是否释放、panic 是否绕过 Done、配置容量和 limiter 实例作用域 |
| 熔断不起作用 | 是否装在客户端、operation、实际错误分类和独立实例；超时不等于远端未提交 |
| 发现无节点 | 服务名、endpoint scheme、advertised 地址、provider权限、watch与连接状态 |
| Trace/metrics 缺失 | contrib、provider/exporter、双端中间件、传播、采样和停止时 flush |
| 事务或资源泄漏 | 所有失败路径、Rows/Body/Close、回滚、cleanup 与后台取消/等待 |
| 运行时 panic | 原始 cause 与覆盖范围；Recovery 不替代根因修复或业务错误处理 |

## 验证方式

在项目允许环境复现并验证修复。需要真实 MySQL、provider 或多实例时使用获准的隔离依赖，不把内存替身当成并发或恢复证明。

生成/编译失败先查看实际工具版本和已生成文件头，不运行无差别 `go get -u`。启动失败检查已取得资源是否关闭；提交异常检查持久事实和 UNKNOWN 契约，避免自动重做业务。

错误日志保留必要 cause 并脱敏。未复现的疑点明确标注，不把猜测写成已确认缺陷。
