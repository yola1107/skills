# 服务注册与发现

版本见[版本基线](version-baseline.md)。固定端点能满足需求时无需注册中心；采用 provider 时，在装配层初始化客户端并注入核心接口。

## 核心边界

`registry.Registrar` 负责注册/注销，`registry.Discovery` 负责发现，Watcher 负责更新订阅。etcd、Consul、Nacos、Kubernetes 等在独立 contrib `/v3` 模块中，按实际 provider 的 README、版本与权限配置，不假设构造参数相同。

装配点通过 `kratos.Registrar(registrar)` 接入注册器；实例 ID、版本、advertised endpoint 和 provider cleanup 按项目处理。注册成功不代表依赖或业务 readiness 成功。

客户端配置 `discovery:///service-name` 和对应 `WithDiscovery`，使用项目约定的传输、TLS、deadline 与[节点选择](selector-patterns.md)。服务名和 endpoint scheme 必须与注册记录一致。

## 运行与验收

- provider 连接与 watcher 随应用生命周期复用。基线正常停止时，`App.Stop` 执行 `BeforeStop → 注销实例 → 取消应用 Context`；`Run` 协调 transport 停止并等待退出，入口随后显式调用 Wire cleanup。
- 业务摘流由应用安排，与服务注销及依赖清理区分。早期失败另按[装配边界](architecture-patterns.md)处理；注销失败保留诊断与未完成的清理责任。
- 明确注册失败、发现空集合、断连重连和陈旧节点时的策略；不要用无界循环掩盖启动失败。
- 验收实例上下线、取消 Watch、空节点、连接关闭和实际地址可达性。读取服务列表不能替代业务 RPC 检查。
- 集群凭据、服务权限与网络范围由项目配置；示例不授权连接生产或外部测试集群。

来源：[注册发现](https://go-kratos.dev/zh-cn/docs/component/registry/)、[应用生命周期](https://go-kratos.dev/zh-cn/docs/component/application/)、[独立模块](https://go-kratos.dev/zh-cn/docs/getting-started/plugin/)。
