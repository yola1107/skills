# OAuth2 中间件

用于已选用 OAuth2 的调用方与资源服务。独立 module 为 `github.com/go-kratos/kratos/contrib/middleware/oauth2/v3`，出现在[核对主干](version-baseline.md#正式版与主干差异)，不属于核心 v3.0.0 发布内容。使用前确认项目所选 module 的实际版本；采用 Kratos 本身不要求增加 OAuth2。

## 客户端凭据

`Client(oauth2.TokenSource)` 获取 access token 并设置 Authorization，内部用 `oauth2.ReuseTokenSource` 复用有效 token。TokenSource 按应用生命周期构造，令牌获取所用 HTTP client 设置有界超时；`Token()` 不接收本次 RPC 的 Context，不能假定 RPC 取消会中断刷新。

HTTP 生成客户端或 Invoke 可安装该中间件；原生 `Do` 的接入方式见[客户端入口](transport-patterns.md#客户端入口与-tls)。使用 `oauth2.Transport` 时在其 Base 配置 TLS。gRPC 流在建流前配置凭据，见[流式调用](streaming-patterns.md)；原生 `credentials/oauth.TokenSource` 可通过 `WithPerRPCCredentials` 接入，保留其 TLS 要求，并在同一 Kratos `WithOptions` 中合并项目的原生 dial options。

## 资源服务校验

`Server(Validator, ...)` 验证 token，将 `*TokenInfo` 放入 Context；通过 `FromContext` 读取。`RequireScopes(...)` 放在 Server 之后，并按 operation 配置需要的全部 scope。认证、scope 与业务对象权限分别在相应边界完成。

模块检查 Active 和非零 Expiry；Issuer、Audience 等字段的存在不代表策略已执行。按项目要求在 Validator 中校验 issuer、audience、主体和必需的到期声明。JWT access token 使用已确定的签名/JWKS 校验实现；此中间件不提供授权服务器、登录或授权码流程。

## Introspection 与缓存

`NewIntrospectionValidator(endpoint, client, ...)` 调用 introspection 端点，可用 `WithBasicAuth` 配置其服务凭据。传入 nil client 会使用 `http.DefaultClient`，模块不额外设置请求超时；使用项目管理的 TLS、超时、Context 与连接清理。

`WithCacheTTL` 只缓存 active 结果，并限制在 token 到期时间内；`WithCacheSize` 限制条目数。缓存命中返回共享的 TokenInfo，按只读对象使用。TTL 内的撤销与权限变化可能尚不可见，按允许的吊销延迟选择 TTL；授权事务仍重验业务权限。

验收无效/过期 token、issuer/audience 策略、scope 不足、令牌服务超时、缓存到期与实际凭据传播。HTTP challenge、gRPC 错误及日志遵守项目协议和脱敏规则，测试使用获准的本地依赖。

来源：[核对主干 OAuth2 说明](https://github.com/go-kratos/kratos/blob/dd0fb7df1e325daf5ffb9c30862be8f1091763eb/contrib/middleware/oauth2/README.md)、[Server](https://github.com/go-kratos/kratos/blob/dd0fb7df1e325daf5ffb9c30862be8f1091763eb/contrib/middleware/oauth2/server.go)、[Introspection](https://github.com/go-kratos/kratos/blob/dd0fb7df1e325daf5ffb9c30862be8f1091763eb/contrib/middleware/oauth2/introspection.go)。
