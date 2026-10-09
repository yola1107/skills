# 第三方来源、版权与许可

本文件集中维护两个 Go 技能的来源、改编关系、版权声明与许可正文。安装或分发技能时一并保留本文件；技能目录内不另存许可证副本。

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

上述上游内容沿用 MIT 许可。Copyright (c) 2025 Addy Osmani；完整条款集中保留于本文的 [MIT License](#mit-license) 小节。

## Anthropic Claude Code Simplifier

- 上游仓库：[anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)。
- 固定上游提交：`f713a7c59b729741282f9c2d9a04e28e2abbd20c`；借鉴日期：2026-10-09。
- 来源：[plugins/code-simplifier/agents/code-simplifier.md](https://github.com/anthropics/claude-plugins-official/blob/f713a7c59b729741282f9c2d9a04e28e2abbd20c/plugins/code-simplifier/agents/code-simplifier.md)。
- `go-code-simplifier/SKILL.md` 借鉴其五条清理原则和简短执行流程，改写为中文 Go Skill：以 Effective Go 与 Go Code Review Comments 替换 JavaScript／React 风格约定，保留本地范围、一字段一行、三组 imports 和行为等价要求；Go 专项检查迁入 `references/go-equivalence.md` 按需读取。未导入上游模型配置、插件注册或自动执行策略。
- 上游插件采用 Apache-2.0；从上述固定提交取得的许可正文逐字节保留于本文的 [Apache License 2.0](#apache-license-20) 小节。已有 Addy Osmani 合并内容的来源与 MIT 许可仍按前节保留。

## samber/cc-skills-golang

- 上游仓库：[samber/cc-skills-golang](https://github.com/samber/cc-skills-golang)。
- 固定上游提交：`8e899e20ff0cd4dc524af3993e4c62d8ee8c5717`；借鉴日期：2026-10-09。
- 参考 [golang-naming](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-naming/SKILL.md)、[golang-code-style](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-code-style/SKILL.md)、[golang-refactoring](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-refactoring/SKILL.md) 及其 identifiers、details、go-tooling、safety-net 参考资料。
- 本地择要中文重述命名去重、复杂条件表达、工具能力边界及按改动路径建立行为测试的建议，合入 `go-code-simplifier/SKILL.md` 与 `references/go-equivalence.md`；风格依据统一为 Effective Go 与 Go Code Review Comments，保留本地三组 imports 和一字段一行默认约定。未导入上游技能、审批／提交编排、覆盖率阈值或可能改变既有行为的强制风格规则。
- 上游采用 MIT 许可；Copyright (c) 2026 Samuel Berthe。完整条款与其他 MIT 来源共用本文的 [MIT License](#mit-license) 小节，版权声明按来源分别保留。

## ECC

- 上游仓库：[affaan-m/ECC](https://github.com/affaan-m/ECC)（原名 `everything-claude-code`）。
- 固定上游提交：`ef648e01899ba3e8dc6371642deaaf64b4477775`；导入日期：2026-10-08。
- `go-reviewer/SKILL.md` 来自 [agents/go-reviewer.md](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/agents/go-reviewer.md)。导入基线提交为 `88e52c1`：Agent 转为 Skill，仅适配元数据和本地参考路径。
- `go-reviewer/references/golang-patterns.md` 的原版 [skills/golang-patterns/SKILL.md](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/skills/golang-patterns/SKILL.md) 逐字节保留在该导入基线中。
- 当前本地修订收敛为中文 Go 审核流程与按需语义参考：补全暂存/未跟踪和目录范围、项目与 module 边界，按契约判断错误和并发生命周期，取消机械严重度阈值，移除有误或非等价的示例及未标版本的通用 lint 配置。保留上游来源和 MIT 许可，不依赖另行安装技能。
- 本次仅导入 Go reviewer 及其直接引用的 Go patterns；未导入 ECC 的命令、hooks、配置或其他技能。
- 上游 [LICENSE](https://github.com/affaan-m/ECC/blob/ef648e01899ba3e8dc6371642deaaf64b4477775/LICENSE) 采用 MIT 许可；Copyright (c) 2026 Affaan Mustafa。完整条款与其他 MIT 来源共用本文的 [MIT License](#mit-license) 小节，版权声明按来源分别保留。

## MIT License

以下完整条款分别适用于上文的 Addy Osmani、samber/cc-skills-golang 与 ECC 来源内容；各版权声明对应其来源，不改变许可归属。

```text
MIT License

Copyright (c) 2025 Addy Osmani
Copyright (c) 2026 Samuel Berthe
Copyright (c) 2026 Affaan Mustafa

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
```

## Apache License 2.0

以下为 Anthropic Claude Code Simplifier 固定提交中的完整许可正文。

```text

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```
