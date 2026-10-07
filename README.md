# skills

本仓库提供用于 Go 项目的 Codex 技能。

- [go-code-simplifier](go-code-simplifier/SKILL.md)：清理指定范围内的 Go 代码，包括测试文件，保持可观察行为不变。

## 使用

将 `go-code-simplifier/` 目录复制到目标项目的 `.agents/skills/` 下，确保入口为 `.agents/skills/go-code-simplifier/SKILL.md`。

在目标项目的 Codex 会话中输入：

```text
$go-code-simplifier 等价行为清理 internal/service，包括测试文件。
```

将 `internal/service` 替换为目标文件或目录。技能遵循目标项目的规则、Go 兼容版本和构建配置；详细清理规则统一维护在对应的 `SKILL.md` 中。
