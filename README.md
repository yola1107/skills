# Go Code Simplifier

本仓库只提供 [go-code-simplifier](go-code-simplifier/SKILL.md)：清理 Go 代码，提高可读性，保持现有行为。

## 使用

将 `go-code-simplifier/` 复制到目标项目的 `.agents/skills/`，将 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 复制到 `.agents/skills/THIRD_PARTY_NOTICES.md`。多个项目共用时可放到 `~/.agents/skills/`，保留相同目录关系。

```text
$go-code-simplifier 清理 internal/service，包括测试，提高可读性，保持行为不变。
```

指定目录时检查全部手写 Go 代码；未指定范围时处理当前改动。风格依据 Go 官方的 [Effective Go](https://go.dev/doc/effective_go)、[Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) 和 [Go Doc Comments](https://go.dev/doc/comment)，遵循项目明确规则与目标 Go 版本。

源码目录需要安装后才进入默认发现范围。修改源码时更新安装副本；更新未出现时重启 Codex。发现位置见 [OpenAI 技能文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。
