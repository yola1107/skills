# skills

本仓库提供用于 Go 项目的 Codex 技能。

- [go-code-simplifier](go-code-simplifier/SKILL.md)：清理指定范围内的 Go 代码，包括测试文件；简化命名、表达式、控制流、重复逻辑和冗余包装，保持可观察行为不变。
- [code-review-and-quality](code-review-and-quality/SKILL.md)：只读审核指定变更或代码范围，给出有证据的质量发现与验证结论。

Go 清理规则统一维护在 `go-code-simplifier`；审核技能保留上游章节、来源署名和参考资料，并补充独立的 Go 专项参考。来源、合并关系、原版基线和版权声明统一见 [第三方来源](THIRD_PARTY_NOTICES.md)。

## 使用

将需要的完整技能目录复制到目标项目的 `.agents/skills/` 下，确保入口为 `.agents/skills/<技能名>/SKILL.md`，如有 `references/` 则一并复制。每个技能独立使用。分发时，在目标项目的第三方声明中保留相应来源与许可。

在目标项目的 Codex 会话中输入：

```text
$go-code-simplifier 等价行为清理 internal/service，包括测试文件。
$code-review-and-quality 审核当前未提交改动，只读报告问题与验证缺口。
```

将 `internal/service` 替换为目标文件或目录。技能遵循目标项目的规则、Go 兼容版本和构建配置；详细清理规则统一维护在对应的 `SKILL.md` 中。
