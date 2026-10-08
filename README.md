# skills

本仓库提供用于 Go 项目的 Codex 技能。

- [go-code-simplifier](go-code-simplifier/SKILL.md)：清理指定范围内的 Go 代码，包括测试文件；简化命名、表达式、控制流、重复逻辑和冗余包装，保持可观察行为不变。
- [go-reviewer](go-reviewer/SKILL.md)：从 ECC 导入的 Go 专项审核，覆盖惯用写法、错误处理、并发、安全和性能；附带上游 Go 模式参考和 MIT 许可证。

Go 清理规则统一维护在 `go-code-simplifier`，Go 审核入口为 `go-reviewer`。审核技能按 ECC 固定提交导入，仅适配 Skill 元数据与本地参考路径。来源、合并关系、原版基线和版权声明统一见 [第三方来源](THIRD_PARTY_NOTICES.md)。

## 使用

将需要的完整技能目录复制到目标项目的 `.agents/skills/` 下，确保入口为 `.agents/skills/<技能名>/SKILL.md`，如有 `references/` 和 `LICENSE` 则一并复制。每个技能独立使用。分发时，在目标项目的第三方声明中保留相应来源与许可。

在目标项目的 Codex 会话中输入：

```text
$go-code-simplifier 等价行为清理 internal/service，包括测试文件。
$go-reviewer 审核当前未提交的 Go 改动，只读报告问题与验证缺口。
```

将 `internal/service` 替换为目标文件或目录。技能遵循目标项目的规则、Go 兼容版本和构建配置；详细清理规则统一维护在对应的 `SKILL.md` 中。
