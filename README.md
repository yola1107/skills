# Go Code Simplifier

本仓库保留两份独立的 Go 简化 skill：

- [go-code-simplifier](go-code-simplifier/SKILL.md)：原版。
- [golang-code-simplifier](golang-code-simplifier/SKILL.md)：按 Claude Code code-simplifier 的架构适配的通用 Go 清理与优化版本。

## 使用

选择需要的版本，将对应的完整目录复制到目标项目的 `.agents/skills/`，或共用的 `~/.agents/skills/`。两份 skill 独立保留，使用时按名称指定。

```text
用 golang-code-simplifier 简化 games/br001，保持现有行为。
```

默认聚焦近期改动；指定目录时检查该目录。改动留在工作区供审阅。

## golang-code-simplifier 文件职责

- [SKILL.md](golang-code-simplifier/SKILL.md)：五项职责、执行流程和可选工具；Go 风格规范集中在“遵循项目规范”一节。
- [Go 等价检查](golang-code-simplifier/references/go-equivalence.md)：涉及特定改写时按需查证，不规定命名或排版风格。
- [golangci.yml](golang-code-simplifier/scripts/golangci.yml)：无项目配置时可选的只读诊断；项目现有配置优先。用法见 skill 的「可选 lint」。

## 设计来源

借鉴 [Claude Code 官方 code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) 的行为保持、清晰优先、尊重项目约定和聚焦改动的思路。未直接采用其中的 JavaScript/React 专用要求；Go 风格由目标项目和社区惯例决定，skill 只补充必要的等价性检查。
