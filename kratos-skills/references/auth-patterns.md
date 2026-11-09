# 认证与 JWT

版本见[版本基线](version-baseline.md)。核心不包含 JWT 中间件；需要 JWT 时使用独立模块 `github.com/go-kratos/kratos/contrib/middleware/jwt/v3`。该模块依赖的 JWT 类型来自 `github.com/golang-jwt/jwt/v5`，第三方库主版本不随 Kratos 改为 v3。OAuth2 TokenSource、introspection 和 scope 接入见[OAuth2](oauth2-patterns.md)。

## 配置认证

- 服务端接入 contrib 的 `Server`；按所选模块版本核对 key function、`WithSigningMethod`、`WithClaims` 与 `WithParserOptions`。
- claims factory 每次返回新对象，避免并发请求共享可变 claims。显式落实项目要求的 issuer、audience、到期和签名算法校验，不假定默认选项覆盖业务策略。
- 成功后通过模块的 `FromContext` 读取 claims，检查存在性与具体类型，再转换为业务需要的可信身份。
- 仅在下游要求服务凭据时使用客户端认证中间件。不要为所有内部 RPC 自动增加 JWT。

公开 operation 使用[中间件 selector](middleware-patterns.md)明确豁免；JWT 证明凭据身份，业务授权仍在用例和必要事务中完成。手写 HTTP 路由、客户端 `Do` 和[流式调用](streaming-patterns.md)按各自入口验证认证确实接入。

## 既有认证协议

已使用 Session、HMAC、mTLS 等机制的项目继续遵守其契约。渠道验签常依赖原始 body、时间窗口、AppID、来源 IP 与当前权限；不能用 JWT 替代或先解码重编码再验签。

签发、刷新、密钥轮换和吊销由应用负责。使用项目的凭据来源与有效期策略；日志和错误正文不包含原始 token、密钥或敏感 claims。

验收有效、过期、错误签名/算法/主体、公开入口与受保护入口，以及业务权限变化。仅 token 解码成功不能证明认证完成。

来源：[官方认证文档](https://go-kratos.dev/zh-cn/docs/component/middleware/auth/)。具体 contrib API 按项目锁定的独立 module 源码核对。
