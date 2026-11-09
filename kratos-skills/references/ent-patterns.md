# Ent 与数据层

Kratos 版本见[统一基线](version-baseline.md)。Ent 是可选的独立 ORM，版本和生成规则按项目固定；使用 Kratos v3 不要求引入 Ent，也不意味着 Ent 的主版本必须是 v3。已有 database/sql 项目优先沿用现状。

## 构造与生成

- data 持有 Ent client，仓储借用它，构造函数返回 cleanup 与错误。装配失败时关闭已取得连接，正常停止时统一清理。
- 若从现有 sql.DB 构造，按 Ent 的 dialect driver API 包装；`ent.Driver` 不能直接接收未经适配的标准库 sql.DB。
- schema 与生成配置是输入，生成实体代码不是手工维护对象；修改后按固定工具版本重新生成并检查差异。
- 服务启动默认只做连接与 schema 兼容预检。schema 创建/升级放在项目明确授权的安装或迁移入口，避免在 `NewData` 中隐式执行 DDL。

## 仓储与事务

接口仍由 biz 使用方定义，返回业务需要的表示；确有差异时才引入 PO 转换。Ent 的 NotFound、约束冲突、取消和连接错误分别映射，查询失败不能被忽略后继续创建记录。

一次原子业务动作使用同一个 Ent transaction，所有实体操作都从该 transaction 派生，不能混用根 client。开始事务后安排回滚清理；每个失败分支保留原始错误，提交错误保留结果未知的可能性。业务所需锁、隔离级别与跨 schema 能力必须由实际实现和数据库证明。

hooks、interceptors、eager loading 和分页按现有需求采用。避免把业务授权隐藏到不易识别的全局 hook，或无界读取整个关系集合。实体对象与 transaction 的关联行为按项目 Ent 版本核对。

## 验证

真实数据库验证唯一约束、回滚、并发锁与提交不确定性。内存或 SQLite 替身只能覆盖其等价的规则，不能证明 MySQL 事务行为。连接池大小和预加载收益依据预算与测量。

来源：[Ent SQL 集成](https://entgo.io/docs/sql-integration/)、[Ent 事务](https://entgo.io/docs/transactions/)、[Kratos Ent 指南](https://go-kratos.dev/zh-cn/docs/guide/ent/)。
