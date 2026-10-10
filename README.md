# Go Code Simplifier

本仓库只提供 [go-code-simplifier](go-code-simplifier/SKILL.md)：清理 Go 代码，提高可读性，保持现有行为。

## 使用

将整个 `go-code-simplifier/` 目录（含 `references/`）复制到目标项目的 `.agents/skills/`；多个项目共用时放到 `~/.agents/skills/`。安装的是副本，本仓库更新后需要重新复制。

```text
用 go-code-simplifier 清理 internal/service，包括测试，提高可读性，保持行为不变。
```

指定目录时检查全部手写 Go 代码；未指定范围时处理当前改动。改动留在工作区，审阅 diff 后自行提交。风格依据 Go 官方的 [Effective Go](https://go.dev/doc/effective_go)、[Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) 和 [Go Doc Comments](https://go.dev/doc/comment)，项目规则可补充或覆盖，新写法以目标 Go 版本为准。

清理整个目录时会通读全部代码；有改动时默认运行一次基线和一次最终验证，按具体风险追加检查。建议交给 subagent 在独立上下文中执行，并选用推理能力较强的模型。
