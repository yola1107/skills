# Go Code Simplifier

本仓库保留两份独立的 Go 简化 skill：

- [go-code-simplifier](go-code-simplifier/SKILL.md)：原版。
- [golang-code-simplifier](golang-code-simplifier/SKILL.md)：按 Claude Code code-simplifier 的架构适配的通用 Go 清理与优化版本。

## 使用

选择需要的版本，将对应的完整目录复制到目标项目的 `.agents/skills/`，或共用的 `~/.agents/skills/`。两份 skill 独立保留，使用时按名称指定。

```text
用 golang-code-simplifier 简化 games/br001，保持现有行为。
```

默认处理未提交的改动；指定目录时处理其中全部手写代码，包括 `_test.go`。改动留在工作区供审阅，不提交。

## golang-code-simplifier 文件职责

只有一个 [SKILL.md](golang-code-simplifier/SKILL.md)，以官方 code-simplifier 为骨架：

- 5 条规则：行为不变（列出 Go 中易变的行为）、遵循 Go 规范（Effective Go、Go Code Review Comments、Go Doc Comments 及命名细则）、简化结构、避免过度简化、范围
- 6 步流程：确定范围、建立基线并通读、逐个文件修改、基于 diff 审核、最终验证、汇报
- 环境中有 `gopls`、`goimports`、`staticcheck`/`golangci-lint`、子 agent 时使用，没有时按手工方式完成

## 设计来源

借鉴 [Claude Code 官方 code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) 的行为保持、清晰优先、尊重项目约定和聚焦改动的思路。未直接采用其中的 JavaScript/React 专用要求；Go 风格由目标项目和社区惯例决定，skill 只补充必要的等价性检查。
