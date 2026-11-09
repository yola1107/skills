# 节点选择与负载均衡

版本见[版本基线](version-baseline.md)。顶层 `selector` 包用于出站节点选择；按 operation 选择中间件使用的是 `middleware/selector`，两者不要混淆。

## 策略与范围

核心提供 `selector/p2c`、`selector/wrr`、`selector/random` 的 builder。根据实例权重、延迟、流量分布和已有策略选择，不凭算法名称推断容量提升。

`selector.SetGlobalSelector(...)` 影响进程内采用该全局 builder 的客户端，只在装配初始化阶段有意设置；请求路径或仓储构造不能偷偷覆盖其他客户端策略。HTTP/gRPC 客户端的 `WithNodeFilter` 与 `WithSubset` 按实际版本配置。

节点筛选依据可信部署元数据与明确路由策略。筛选后为空时返回真实不可用错误，不绕过区域、租户或授权约束随机转发。

## 自定义实现

先读锁定版本的 `Selector`、`Builder`、`Node`、`WeightedNode`、`DoneFunc` 和 rebalance 契约，再实现需要的最小扩展。选择后的完成回调用于反馈结果；实例变更与并发请求需要保持状态一致。

验证节点增删、空集合、并发、完成反馈和取消行为。负载均衡不提供请求幂等；选择另一个实例重试写入仍需业务授权和持久防重。

来源：[路由与负载均衡](https://go-kratos.dev/zh-cn/docs/component/selector/)、[v3 selector 源码](https://github.com/go-kratos/kratos/tree/v3.0.0/selector)。
