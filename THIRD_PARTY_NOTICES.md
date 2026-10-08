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

## Anthropic Claude Code Simplifier

- 上游仓库：[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)。
- 固定上游提交：`f713a7c59b729741282f9c2d9a04e28e2abbd20c`；借鉴日期：2026-10-09。
- 来源：[plugins/code-simplifier/agents/code-simplifier.md](https://github.com/anthropics/claude-plugins-official/blob/f713a7c59b729741282f9c2d9a04e28e2abbd20c/plugins/code-simplifier/agents/code-simplifier.md)。
- `go-code-simplifier/SKILL.md` 借鉴其五条清理原则和简短执行流程，改写为中文 Go Skill：替换 JavaScript／React 约定，保留本地范围、一字段一行和行为等价要求；Go 专项检查迁入 `references/go-equivalence.md` 按需读取。未导入上游模型配置、插件注册或自动执行策略。
- 上游插件采用 Apache-2.0；[go-code-simplifier/LICENSE](go-code-simplifier/LICENSE) 从上述固定提交逐字节保留。已有 Addy Osmani 合并内容的来源与 MIT 许可仍按前节保留。

## samber/cc-skills-golang

- 上游仓库：[samber/cc-skills-golang](https://github.com/samber/cc-skills-golang)。
- 固定上游提交：`8e899e20ff0cd4dc524af3993e4c62d8ee8c5717`；借鉴日期：2026-10-09。
- 参考 [golang-naming](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-naming/SKILL.md)、[golang-code-style](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-code-style/SKILL.md)、[golang-refactoring](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-refactoring/SKILL.md) 及其 identifiers、details、go-tooling、safety-net 参考资料。
- 本地择要中文重述命名去重、复杂条件表达、工具能力边界及按改动路径建立行为测试的建议，合入 `go-code-simplifier/SKILL.md` 与 `references/go-equivalence.md`；保留本地三组 imports 和一字段一行约定。未导入上游技能、审批／提交编排、覆盖率阈值或可能改变既有行为的强制风格规则。
- 上游采用 MIT 许可；[go-code-simplifier/LICENSE.samber](go-code-simplifier/LICENSE.samber) 从固定提交逐字节保留。Copyright (c) 2026 Samuel Berthe；与前述 Apache-2.0 和已有 MIT 来源分别保留。

## ECC

- 上游仓库：[affaan-m/ECC](https://github.com/affaan-m/ECC)（原名 `everything-claude-code`）。
- 固定上游提交：`ef648e01899ba3e8dc6371642deaaf64b4477775`；导入日期：2026-10-08。
- `go-reviewer/SKILL.md` 来自 [agents/go-reviewer.md](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/agents/go-reviewer.md)。导入基线提交为 `88e52c1`：Agent 转为 Skill，仅适配元数据和本地参考路径。
- `go-reviewer/references/golang-patterns.md` 的原版 [skills/golang-patterns/SKILL.md](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/skills/golang-patterns/SKILL.md) 逐字节保留在该导入基线中。
- 当前本地修订收敛为中文 Go 审核流程与按需语义参考：补全暂存/未跟踪和目录范围、项目与 module 边界，按契约判断错误和并发生命周期，取消机械严重度阈值，移除有误或非等价的示例及未标版本的通用 lint 配置。保留上游来源和 MIT 许可，不依赖另行安装技能。
- 本次仅导入 Go reviewer 及其直接引用的 Go patterns；未导入 ECC 的命令、hooks、配置或其他技能。
- 上游 [LICENSE](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/LICENSE) 原样保存在 [go-reviewer/LICENSE](go-reviewer/LICENSE)。Copyright (c) 2026 Affaan Mustafa；MIT License。
