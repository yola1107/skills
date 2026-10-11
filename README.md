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

- 5 条原则：保留行为、遵循 Go 规范、提升清晰度、保持平衡、聚焦范围
- 清理检查：覆盖字段、参数、局部变量等命名，以及控制流、职责和冗余，核对 Go 等价性前提
- 6 步流程：定范围与基线、通读并列清单、按函数批次修改、验证等价、分别验收行为等价性与清理充分性、按实际结果汇报
- 按需使用 `rg`、ast-grep、gopls 和项目已有格式/lint 工具；整包清理由独立 agent 只读复核，修正后只复核影响处

## 设计来源

借鉴 [Claude Code 官方 code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) 的行为保持、清晰优先、尊重项目约定和聚焦改动的思路。未直接采用其中的 JavaScript/React 专用要求；Go 风格由目标项目和社区惯例决定，skill 只补充必要的等价性检查。
