# 第三方来源与版权

## Addy Osmani

本节记录原 `code-review-and-quality/` 和 `code-simplification/` 的 Addy Osmani 来源与许可。两个原技能现已移除；原清理技能中适用于 Go 的规则已择要合并到 `go-code-simplifier/`，下列来源与许可声明随合并内容保留；`go-code-simplifier/` 其余内容的既有来源与许可不因本次合并而改变。

- 上游仓库：https://github.com/addyosmani/agent-skills
- 上游提交：`1401c8b8030e023baeebb31781a6653fe8e93026`
- 原版导入提交：`b119682`；导入日期：2026-10-08。
- 原版技能、直接引用的共享 checklist 与许可证均逐字节保存在该提交的 `addyosmani/` 下。
- 平铺基线提交为 `0b07d7d`：审核技能的两份原版 checklist 放在其目录内，入口仅修正两处相对路径；其他上游正文、示例和来源署名保持原样。
- 导入后的定制以该基线逐项修改：保留原章节与来源署名，修正执行边界、非等价示例和技术栈适用条件，并为两个技能分别增加独立的 Go 专项 reference。
- 原 `code-review-and-quality/`、`code-simplification/` 及其参考资料均已移除；清理技能中有用且不重复的规则和直返反例合并到 `go-code-simplifier/SKILL.md`。
- 原清理技能另注明受 [Claude Code Simplifier 插件](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md)启发，此处保留该来源署名。

上述上游内容沿用 MIT 许可。分发包含合并内容的 Go 清理技能时一并保留以下版权与许可声明。

MIT License

Copyright (c) 2025 Addy Osmani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## ECC

- 上游仓库：[affaan-m/ECC](https://github.com/affaan-m/ECC)（原名 `everything-claude-code`）。
- 固定上游提交：`ef648e01899ba3e8dc6371642deaaf64b4477775`；导入日期：2026-10-08。
- `go-reviewer/SKILL.md` 来自 [agents/go-reviewer.md](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/agents/go-reviewer.md)。将 Claude Code Agent 转为 Skill：移除 `tools`、`model` 字段，限定 description 的审核触发范围，加入许可与来源元数据，末尾跨技能引用改为本目录内的参考链接。审核正文及严重程度规则保持上游内容。
- `go-reviewer/references/golang-patterns.md` 逐字节保留 [skills/golang-patterns/SKILL.md](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/skills/golang-patterns/SKILL.md)，作为按需阅读的参考，不依赖另行安装技能。
- 本次仅导入 Go reviewer 及其直接引用的 Go patterns；未导入 ECC 的命令、hooks、配置或其他技能。
- 上游 [LICENSE](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/LICENSE) 原样保存在 [go-reviewer/LICENSE](go-reviewer/LICENSE)。Copyright (c) 2026 Affaan Mustafa；MIT License。
