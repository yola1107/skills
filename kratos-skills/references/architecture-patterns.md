# 架构与 Wire 装配

版本遵循[统一基线](version-baseline.md)。先对照项目选定的布局与现有实现；Kratos 不要求每个服务独立 module，也不要求固定数量的包。

## 分层

| 层 | 职责 | 常见依赖 |
| --- | --- | --- |
| server | HTTP/gRPC 构建、注册和传输中间件 | service、配置、传输组件 |
| service | 协议对象、形状校验、业务调用与错误映射 | biz、生成协议 |
| biz | 用例、授权、不变量、状态转换及所需接口 | 自有类型、纯规则 |
| data | SQL、缓存、下游 HTTP/RPC 与外部编码 | biz、数据库和客户端 |
| cmd | 参数、资源构造、Wire 与应用生命周期 | 各层 |

源码依赖为 `service → biz ← data`，运行时 biz 通过接口调用 data。接口放在实际使用方；用例可以是具体 `UserUsecase`，不必再包一层接口。简单查询保持浅层，复杂业务按共同变化的规则组织。

模型在传输、业务、持久化表示确有差异时转换。业务对象不携带数据库事务或 protobuf 类型；按项目约定控制业务代码对日志与框架的依赖。

## Wire

- 沿用项目的 provider 组织；Layout 常用 `wire.NewSet(...)` 汇总各层构造函数，data 构造返回 biz 所需接口。
- `cmd/<binary>/wire.go` 使用 `//go:build wireinject`；常见 injector 写法是 `panic(wire.Build(...))`，保持 `github.com/google/wire` import。
- injector 的参数应与实际构造输入一致，例如配置、`*slog.Logger`；返回值与顶层 provider 一致，资源构造链可返回 cleanup 和 error。
- `newApp` 返回 `*kratos.App`，在装配点设置 `kratos.Server(...)` 与生命周期选项。
- `wire_gen.go` 由项目固定的 Wire 命令生成；修改 provider 后重新生成并复核资源失败路径，不能手改生成文件。

provider 返回具体类型而消费方需要接口时，使用 `wire.Bind`；已返回所需接口时无需绑定。是否绑定取决于类型关系，与实现数量无关。Wire 用于编译期装配，不引入运行时服务定位器。

Wire 返回的 cleanup 由入口调用，`kratos.App` 不会代为执行。入口顺序示意（变量及返回值沿用项目）：

```text
app, cleanup, err := wireApp(ctx, cfg)
if err != nil {
    return err
}
defer cleanup()
return app.Run()
```

这样 `Run` 启动失败返回与正常停止返回都经过 cleanup；构造链中途失败则由生成的 Wire 代码清理此前已成功构造的资源。检查实际生成结果和入口，不能仅看 provider 声明。

## 生命周期与失败清理

基线的 App 默认处理 SIGTERM、SIGQUIT、SIGINT；应用统一安排摘流、停止、等待和依赖关闭。`StopTimeout` 只为 transport 的 Stop 提供超时 Context，不是整段退出流程的总预算；BeforeStop/AfterStop 等 hook、后台工作和 cleanup 按自己的责任设置边界。AfterStart 或注册完成也不证明业务 readiness。

`Run` 部分启动错误会在完整停止协调前返回，入口 defer 只保证调用 cleanup，不保证 transport 已停止。例如构建实例时调用 HTTP `Endpoint()` 可能提前取得 listener；随后其他 endpoint 或启动 hook 失败时，SQL 的 cleanup 无法释放它。

存在这种路径时，把预先取得的 listener 纳入资源所有权，例如显式创建并传入 `http.Listener`，保留直接 Close 的失败清理路径；尚未进入 Serve 的 listener 不能只依赖 Shutdown。已运行的 transport 和后台工作则先有界停止并等待，再关闭数据连接。按实际使用的 endpoint、hook、注册器路径验证早期失败，不能假定任何 `Run` 返回都已完成全部清理。流式退出与客户端连接归属分别见[流式调用](streaming-patterns.md)和[连接清理](transport-patterns.md#连接与资源归属)。

上述边界依据[基线 App 生命周期源码](https://github.com/go-kratos/kratos/blob/v3.0.0/app.go)与[HTTP 生命周期源码](https://github.com/go-kratos/kratos/blob/v3.0.0/transport/http/server.go)；采用其他 v3 版本时重新核对对应实现。

## 资源与事务

Data 管理长生命周期连接，仓储借用连接。构造中途失败时立即清理已取得的资源；成功后由装配点持有 cleanup。关闭顺序先停止接入和后台工作，再关闭数据库、客户端及 telemetry provider。

业务定义原子动作，data 用同一事务完成。多个仓储各自提交不能替代跨表或跨 schema 的一个事务。锁序、隔离级别、提交未知、幂等和恢复均属于行为契约；每层的 CRUD 模板不能证明这些行为正确。

数据库使用现有方案；采用 Kratos 或 Wire 本身不要求改用 Ent。数据库安装与升级的执行入口按项目约定安排。

来源：[官方布局](https://go-kratos.dev/zh-cn/docs/intro/layout/)、[Wire 指南](https://go-kratos.dev/zh-cn/docs/guide/wire/)、[官方模板](https://github.com/go-kratos/kratos-layout)。模板应固定项目认可的版本后再参照。
