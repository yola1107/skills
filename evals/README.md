# 两个 Go Skill 的评测

这里的输入与断言用于真实模型对照，尚未随代码自检自动执行。`tests/` 的确定性检查只证明文件结构与用例自身有效，不证明模型效果。评测材料不在两个技能入口中引用，避免把验收答案作为日常执行指令加载。

## 固定输入

- [cleanup](fixtures/cleanup/cleanup.go)：正确的代码，包含可清理的冗余转抄，以及失败部分值、defer 读局部 err（含 panic 展开顺序）、短路、nil／空、复制所有权与精确容量、错误身份、有限 goroutine、typed nil 和 caller 约束。配套测试在原版应全部通过。
- [boundaries](fixtures/boundaries/io.go)：正确的 HTTP 状态／读取上限／关闭责任、Scanner/Rows 错误、日志脱敏、有效自定义 TLS 验证及 unsafe 指针样例。TLS 测试通过 net.Pipe 执行内存握手，HTTP 使用内存 RoundTripper，不监听端口或访问外网；Rows 使用消费者接口桩而非真实数据库驱动。
- [access](fixtures/access/access.go)：刻意使用 `||` 违反声明中的 AND 授权契约。配套测试在原版应失败，修复成符合契约的实现后应通过；不要把这个预置缺陷当作本仓库自身待修的问题。

带 `setup_edits` 的用例由监督器在复制 fixture 后、建立受审基线前逐项执行精确替换：`path` 相对 fixture，每个 `before` 必须恰好匹配一次，再替换成 `after`，之后运行 gofmt；不可修改可信测试。替换失败即停止，不能模糊匹配。`review-boundary-defects` 的八项变体用于验证漏报，`untrusted-review-note` 插入的伪造指令只作为受审数据。完成准备后，模型仅看到 fixture、指定技能、前置消息与 prompt，不提供 cases.json、setup_edits 或验收答案。

提示词、前置会话和验收标准见 [cases.json](cases.json)。路径相对本仓库；准备好副本后，以副本作为实际任务目录。此 JSON 是本仓库的评测清单，不假定某个宿主自动识别或执行它。

## 对照流程

为每个用例创建独立工作目录，复制对应 fixture 和待测技能版本，保留外层 THIRD_PARTY_NOTICES.md 及完整 references。每轮固定模型、推理设置、提示词、输入、权限、工具链和构建环境；分别运行无技能、修改前技能和修改后技能。组合用例按清单加载两个技能，不额外引入其他技能或项目规则。

每次使用全新会话，仅注入该用例列出的前置消息，再发送本轮提示词。无技能基线使用相同任务语义，只移除技能选择标记。确认实际加载了待测版本，不能只看安装路径。建议对关键用例重复运行，记录每次真实输出，不以单次成功概括稳定性。

保留原始 fixture 和可信测试副本在模型可编辑工作目录之外。执行后检查完整 diff、文件清单、工作树与 Git 状态，用可信原测试对结果再次验证；不能因为模型删改、放宽或跳过断言而给通过。只读用例比较执行前后原工作树、索引和 HEAD，并检查工具轨迹中的外部写入。评测监督器在模型执行结束后进行独立验证，不把这些监督器操作算作模型行为。

## 验收与记录

逐项记录 PASS／FAIL／未执行及具体文件、命令或输出证据。行为回归、未授权修改或越界外部操作为单独失败，不能由清晰度分数抵消。只读用例不因没有修改而扣分；清理用例允许保留有具体契约理由的代码，不能要求删除行数达标。

同时记录误报、漏报、范围覆盖、人工判断的清晰度收益、工具调用次数和实际可获取的时间／token 数据。没有遥测就标明缺失，不估算冒充记录。结果保存在仓库外的评测工作目录，不预填通过率。

清理夹具还验证 `Run` 在工作函数 panic 时记录 nil 一次并保留原 panic 与展开顺序；`CopyBytes` 的输出容量等于输入长度，而不是输入容量。去掉 defer 或增加返回容量的变体仍能通过旧十项测试，但会被新增的对应契约测试检出；恢复源码后重新通过。

新增自检逐个验证八项边界缺陷：有效原版通过、变体能编译且指定契约测试失败、还原后通过；另验证非法 uintptr 拆分能编译但触发预期 vet 诊断，以及改为普通索引仍通过。vet 反例不是确定的运行时崩溃复现，不能混计为行为测试。提示注入用例这里只验证输入构造，不声称模型已抵抗注入。

当前用例未覆盖 TLS 会话恢复、真实 DNS/代理/出口与数据库驱动、加密算法审计、依赖漏洞联网扫描、性能基准对照、cgo、不同语言版本、多 module／go.work、本地 replace、符号链接／硬链接、受限服务环境与大规模真实项目；需另补场景才能评价这些能力。文档引用检查也不等于外链联网可达性验证。

流程参考 [Agent Skills 评测指南](https://agentskills.io/skill-creation/evaluating-skills)。

## 测试结果汇总

用 [go_test_summary.py](../scripts/go_test_summary.py) 从一次 `go test -json` 的完整 stdout 生成统计。工具只读日志，不运行命令、不加载依赖，也不替代项目验证入口。逐条保留 `(package, test, occurrence)` 与包执行编号；`-count=N` 的重复终结事件按执行次数计数，不去重成“只运行一次”。顶层 `Test`、子测试、Example、Fuzz、Benchmark 和包结果分别列出，不能相加后称为顶层通过数。

在已授权的隔离验证目录运行测试，先将 `SKILLS_REPO` 设为本仓库的实际绝对路径，`EVIDENCE_DIR` 设为新建的仓库外证据目录。下面以完整套件为例；定向 `-run`、race、构建变体和前后基线各用独立日志，保持真实选择条件，不替换项目已有入口：

```sh
if go test -json -count=1 -timeout=60s ./... >"$EVIDENCE_DIR/go-test.jsonl" 2>"$EVIDENCE_DIR/go-test.stderr"; then
    test_exit=0
else
    test_exit=$?
fi
printf '%s\n' "$test_exit" >"$EVIDENCE_DIR/go-test.exit-code"
python3 "$SKILLS_REPO/scripts/go_test_summary.py" \
    "$EVIDENCE_DIR/go-test.jsonl" --exit-code "$test_exit" \
    >"$EVIDENCE_DIR/go-test.summary.json"
```

必须记录 Go 进程的原始退出码，不能用 `tee` 或汇总工具的退出码冒充；stderr 独立保留，旧工具链的编译错误可能不在 JSON stdout 内。报告数量直接取摘要中的 `counts`，失败身份取 `test_results`／`package_results` 的 fail 记录，未完成用例取 `unfinished_tests`；失败原因仍要读完整日志。两组失败数相同不代表失败集合或原因相同。日志可能含敏感数据，保留在获授权的证据位置，不直接提交到公开仓库。

汇总工具退出码：`0` 为观察到测试通过且日志完整、无测试／包跳过；`1` 为进程、包、测试或构建存在失败；`2` 为记录不完整、未知退出状态、无测试通过、存在测试／包跳过或输入错误，不应报全绿。JSON 的 `status` 和 `complete` 分别表达结果与已观察事件完整性；即使已确认失败，也可能同时存在未完成测试。包无测试和测试选择为空不算执行通过。Benchmark 不提供普通测试通过证据；缓存日志只证明对应历史执行，需要新执行证据时用 `-count=1`。

`complete=true` 不证明覆盖全部请求范围：日志若整段漏掉某个包／测试，单看剩余事件可能无法识别。已知预期包时可重复传 `--expect-package <import-path>`，再独立核对预期测试身份及命令选择范围。仓内夹具自检核对确定的顶层测试名称和次数，而不仅是总数。日志缺失、格式不支持或截断时保留缺口，不猜测数量；统计器也不判断失败是否既有、是否构成业务回归，或 Skill 的模型执行质量。
