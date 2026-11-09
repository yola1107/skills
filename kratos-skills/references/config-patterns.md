# 配置与资源替换

版本见[版本基线](version-baseline.md)。优先保留项目现有配置格式、加载与严格校验；Kratos 不要求配置由 Proto 定义，也不要求接入远程配置中心。

## 核心 API

- `config.New(config.WithSource(...))` 组合配置源；文件使用 `config/file`，环境变量使用 `config/env`。
- 检查 `Load()`、`Scan(&target)`、`Value(key)` 的类型转换错误；可用 `config.Get[T](cfg, key)` 读取已知类型。
- 输入格式对应的 codec 必须已注册，加载顺序和同名键覆盖规则要用实际项目样本核对。密码等私密值由项目指定入口提供，不写入公开示例或日志。
- 需要 Watch 时检查注册错误，回调校验完整新值后再发布；持有 Config 的装配点最终调用 `Close()` 释放 watcher。

单文件配置可以满足简单服务；多个配置源只在确有部署或覆盖需求时采用。严格 unknown-field、缺字段或环境变量展开规则不能因更换 loader 而丢失。

布尔占位符的默认解析有[版本差异](version-baseline.md#正式版与主干差异)。例如 `"${ENABLED:true}"` 应同时核对解析后的实际类型与目标字段：`Value.Bool()` 能转换字符串，不代表 `Scan` 到 bool 字段也会成功。`WithResolveActualTypes` 会影响其他值的类型，按项目样本选择，不为修一个字段全局改变配置语义。

## 动态配置

Watch 通知不等于业务更新已经原子生效。基线先更新原始配置值，再调用 Observer；回调没有拒绝或回滚原始值的接口。业务读取独立的已验证快照，避免一边在回调中拒绝无效值，一边又从原始 Config 读取它。连接池、TLS、密钥或业务规则变化时，先完成校验与新资源准备，再按项目的锁、revision 或快照约定切换，最后清理旧资源。

冻结交易、Session 或原局引用原始配置事实时，恢复按原证据处理；不能用当前配置覆盖旧快照。复杂资源不适合热更新时，在启动时校验并通过重启应用更新。

etcd、Consul、Nacos、Kubernetes 等 provider 在独立 contrib 模块中。按所选 `/v3` module 的实际 API 实现认证、watch、重连与关闭，不能把一个 provider 的构造参数套给其他 provider。

来源：[配置文档](https://go-kratos.dev/zh-cn/docs/component/config/)、[独立模块](https://go-kratos.dev/zh-cn/docs/getting-started/plugin/)。
