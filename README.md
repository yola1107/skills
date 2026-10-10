# skills

本仓库提供用于 Go 项目的 Codex 技能。

- [go-code-simplifier](go-code-simplifier/SKILL.md)：清理指定范围内的 Go 代码，包括测试文件；简化命名、表达式、控制流、重复逻辑和冗余包装，保持可观察行为不变。
- [go-code-review](go-code-review/SKILL.md)：基于 ECC 并提炼 samber/cc-skills-golang 规则的 Go 专项审核，覆盖正确性、错误契约、并发和资源生命周期、测试质量、可维护性、安全及性能；附带按需参考。

Go 清理入口为 `go-code-simplifier`，Go 审核入口为 `go-code-review`。两者遵循项目约定及相同的默认可读性规则；各自完整维护执行边界和按需参考，可独立使用。审核技能按固定上游版本择要修订，沿具体契约核实发现，避免把风格模式直接当成缺陷。来源、合并关系、原版基线、版权声明与许可正文统一见 [第三方来源](THIRD_PARTY_NOTICES.md)。

## 使用

将需要的完整技能目录及其 `references/` 复制到目标项目的 `.agents/skills/` 下，确保入口为 `.agents/skills/<技能名>/SKILL.md`。同时将根目录的 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 复制到 `.agents/skills/THIRD_PARTY_NOTICES.md`，集中随附来源、版权与许可。每个技能独立使用，分发时一并保留这份声明。单独安装一个技能也需要这份外层声明；不要只打包技能子目录而遗漏它，目录间相对位置应保持不变。

在目标项目的 Codex 会话中输入：

```text
$go-code-simplifier 等价行为清理 internal/service，包括测试文件。
$go-code-review 审核当前未提交的 Go 改动，只读报告问题与验证缺口。
$go-code-review 审核 internal/service，并修复已确认缺陷；不做范围外风格整理，不提交或推送。
```

将 `internal/service` 替换为目标文件或目录。技能遵循目标项目的规则、Go 兼容版本和构建配置；详细清理规则统一维护在对应的 `SKILL.md` 中。

## 模式与验证

只读审核、已授权缺陷修复和行为等价清理是不同模式；同时加载两个技能不扩大权限。本轮明确的只读要求或范围限制优先于历史授权。默认风格是本仓库约定，不代表 Go 官方强制规则。

在本仓库根目录运行离线自检（Python 3.9+、Git、Go 1.22+）：

```sh
python3 -B -m unittest discover -s tests -v
# 可选 race 检查需要当前平台支持 race 及可用 C 编译器：
SKILLS_RUN_RACE=1 python3 -B -m unittest discover -s tests -v
```

自检检查基本入口字段、仓内文档引用和分发文件，并在临时目录复现 Git 查询边界、运行 Go 契约测试及 vet；另检查八种非等价变换（含 panic 时的 defer 与精确切片容量）及八种安全／I/O 变体会触发指定测试失败、预置缺陷修复后通过，并验证非法 uintptr 拆分的 vet 诊断及等价的安全指针改写。TLS 握手使用内存管道，HTTP／迭代场景用测试替身，不访问外部服务。所有预期失败均由自检明确断言，不代表忽略失败；不会安装依赖、执行模型或修改目标项目。缺失工具会明确报告跳过，不能算作完整验证通过。

[评测说明](evals/README.md) 提供固定输入、提示词和验收标准，用于对比无技能、旧版与新版的真实执行。确定性自检通过不代表模型已经通过评测，也不证明未知项目中的所有转换等价。评测与自检文件不需要安装到目标项目。

测试结果使用 [结构化汇总工具](scripts/go_test_summary.py)，不通过手工数行或搜索 `PASS` 汇总。工具区分顶层测试、子测试、包结果、重复执行与不完整日志；用法和退出码见 [评测说明](evals/README.md#测试结果汇总)。设置 `SKILLS_TEST_EVIDENCE` 为仓库外的目录，可在自检时保留每次 Go 测试的完整 stdout、stderr、命令、退出状态和机器生成的摘要。该工具为仓库维护／评测辅助，不是安装技能的额外依赖。
