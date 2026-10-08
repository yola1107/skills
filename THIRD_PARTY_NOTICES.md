# 第三方来源与版权

本文件记录 `code-review-and-quality/` 及原 `code-simplification/` 的 Addy Osmani 来源与许可。原清理技能中适用于 Go 的规则已择要合并到 `go-code-simplifier/`，下列来源与许可声明随合并内容保留；`go-code-simplifier/` 其余内容的既有来源与许可不因本次合并而改变。

- 上游仓库：https://github.com/addyosmani/agent-skills
- 上游提交：`1401c8b8030e023baeebb31781a6653fe8e93026`
- 原版导入提交：`b119682`；导入日期：2026-10-08。
- 原版技能、直接引用的共享 checklist 与许可证均逐字节保存在该提交的 `addyosmani/` 下。
- 平铺基线提交为 `0b07d7d`：审核技能的两份原版 checklist 放在其目录内，入口仅修正两处相对路径；其他上游正文、示例和来源署名保持原样。
- 导入后的定制以该基线逐项修改：保留原章节与来源署名，修正执行边界、非等价示例和技术栈适用条件，并为两个技能分别增加独立的 Go 专项 reference。
- 当前仅保留审核技能及其参考资料；原 `code-simplification/` 入口与 Go 参考已移除，有用且不重复的规则和直返反例合并到 `go-code-simplifier/SKILL.md`。
- 原清理技能另注明受 [Claude Code Simplifier 插件](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md)启发，此处保留该来源署名。

上述上游内容沿用 MIT 许可。分发审核技能或包含合并内容的 Go 清理技能时一并保留以下版权与许可声明。

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
