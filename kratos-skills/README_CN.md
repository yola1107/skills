# Kratos Skills — v3

基于 [lwx-cloud/kratos-skills](https://github.com/lwx-cloud/kratos-skills) 维护的本地 Kratos v3 参考技能。上游声明采用 MIT 许可，见[上游许可](https://github.com/lwx-cloud/kratos-skills/blob/main/LICENSE)。

入口是 [SKILL.md](SKILL.md)，按问题导航至 23 个专题与共享的[版本基线](references/version-baseline.md)。只加载当前任务相关资料，仓库规范、固定依赖和执行权限优先。

本版统一核心 v3 API、slog 和独立 contrib 模块，替换无效示例，收紧过度绝对的架构要求。数据库、生成器、注册中心与遥测按项目实际需求选择。

调用 `$kratos-skills` 并说明具体任务；安装、恢复与上游比较见[使用说明](getting-started/claude-code-guide.md)。框架用法查[中文官方文档](https://go-kratos.dev/zh-cn/docs/)，行为与业务约束按项目锁定源码及契约确认；文档不能替代集成验收。
