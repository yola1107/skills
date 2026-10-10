# Go 模式与审核边界

基于 ECC 与 samber/cc-skills-golang 的选定规则。仅阅读目标相关的小节，按实际契约、调用路径和目标 Go 版本核实；模式或诊断本身不构成缺陷。来源与许可集中于仓库外层声明。

## 错误与返回值

- 包装错误会改变直接比较、对外文本和 API 暴露的原因；按调用方需求选择错误链。errors.Is／As 适用于包装链，确定的 sentinel 可直接比较；忽略 error 需有实际处理或最佳努力契约，并说明非显然的理由。
- 接口持有 typed nil 时仍有动态类型；追踪返回、nil 分支和方法调用，nil receiver 可以被方法正确支持。
- io.Reader.Read 可同时返回数据与错误，io.EOF 按接口约定原样返回。如下转发正确，无需补包装：

```go
func Relay(r io.Reader, dst []byte) (int, error) {
	return r.Read(dst)
}
```

- guard 可能有意清空失败部分值，defer 也可能读取局部 err。检查直返、错误优先级和部分成功结果；持久化、事务提交、Flush／Close 错误可能影响成功契约。
- 检查协议状态与迭代结束错误：[http.Client.Do](https://pkg.go.dev/net/http#Client.Do) 的非 2xx 不自动返回 error，是否失败按业务协议判断；[Rows.Err](https://pkg.go.dev/database/sql#Rows.Err) 与 [Scanner.Err](https://pkg.go.dev/bufio#Scanner.Err) 区分正常结束和读取失败。检查响应 Body、Rows 等在成功、失败与提前退出时的关闭责任；责任已转移时不提前关闭，不为连接复用无限量读完不可信响应。
- 核对求值次数、顺序与短路；未使用结果仍可能含外部效果，类型断言、索引或 nil 访问也可能产生原有 panic。
- 沿可达入口核对校验职责、调用前提和失败前的副作用；局部 guard 的存在或缺失均不能独立证明安全或缺陷。

## 共享、集合与复制

- slice／map／pointer 及含引用字段的结构可能共享可变数据，append 可能复用底层数组。按借用、转移或独立所有权判断克隆需要；保留 nil／空集合、长度、容量、顺序及 JSON 差异。
- bytes.Buffer.Bytes 返回底层数组别名；归还或复用 buffer 前，独立返回结果需复制，借用 API 则保留生命周期契约：

```go
func CopyResult(buf *bytes.Buffer) []byte {
	return bytes.Clone(buf.Bytes())
}
```

- 检查值接收者、赋值、返回和 range 是否复制已使用的 Mutex、RWMutex、Once、WaitGroup、typed atomic 等不可复制值。普通 pointer／channel 字段只复制引用，不能当作复制锁状态。核对可变状态的权威来源与修改入口；快照、缓存和恢复证据也可能有独立职责。

- 涉及 [unsafe.Pointer](https://pkg.go.dev/unsafe#Pointer)、uintptr、系统调用或跨语言指针时，核对允许的转换形式、对象范围／布局、存活与所有权。uintptr 不保持对象存活；提取中间变量可能破坏必须在同一表达式或调用参数中完成的转换。cgo 另核对 [Go/C 指针传递与保留规则](https://pkg.go.dev/cmd/cgo#hdr-Passing_pointers)，保留前导注释不代表运行时安全。vet、race 或 checkptr 通过均不能替代这些约束。

## Context、同步与资源

- 从创建、成功、失败、取消到关闭追踪 owner 和完成协议。有限 goroutine 可自行返回；阻塞路径须能按契约退出，WaitGroup 等待但不取消，登记须早于 Wait 可能观察到零计数的时点。
- Context 传到实际阻塞操作；外围 select 无法中断已阻塞的非 Context 调用。中途改用 Background／TODO 可能丢失取消、截止或值；脱离请求的后台任务须有独立生命周期。派生 Context 的取消责任覆盖各退出路径，除非已转移；循环 defer cancel 可能延长资源占用。
- 使用 errgroup 核对首错传播与等待路径；errgroup.WithContext 的派生 Context 在 Wait 返回时也会取消，后续阶段核对使用的 Context。Context values 用于请求元数据，检查隐藏业务参数或 key 冲突的实际影响。
- 核对 channel 收发、关闭所有权、背压及结果通知；退出但未完成通知可能使调用方阻塞。select 不保证优先选择取消，sync.Once 不能证明已无发送者；传 pointer 或 slice 可是合法所有权转移。
- worker pool／fan-out 核对输入结束、下游停读、首错与取消时的退出协议，以及并发规模的实际边界。
- 锁覆盖实际不变量，锁内 I/O 可能有必要。单字段 atomic 不自动保护多字段状态；sync.Map 按写一次多读或分离 key 等访问模式判断。sync.Once 不自动重试初始化失败。
- defer 登记求值与闭包执行时读取不同；核对捕获、顺序和 panic／recover。循环体提取可能改变解锁、关闭或回滚时点，保留收尾协议。

## 接口与职责

接口按消费者当前所需能力设计，返回具体类型或接口按暴露能力与兼容判断；零值可用性按构造与资源契约判断，nil map 读取和写入不同。检查接收者、方法集、嵌入、公开兼容和反射／生成引用；仓内调用或初始化路径不证明所有公开入口遵守相同前提。核对职责与依赖方向，合并同形逻辑前比较输入、失败、顺序和责任 owner；承担转换、同步、事务或兼容的包装有价值。结构问题须说明当前维护成本，不能由行数、目录布局、mock 或抽象数量推断。

cgo 前导注释、构建约束和工具指令参与编译或生成，不能当作普通说明删移。核对 `import "C"` 与前导注释的关联；禁用 cgo 的测试不覆盖这些文件，需按涉及的构建条件验证或说明缺口。

## 测试契约与生命周期

- 断言覆盖输出、错误、状态与副作用；关注变更的成功、失败和边界路径。测试形式、断言库及覆盖率不能代替契约证据。
- 并行测试核对环境、cwd、全局状态、固定端口和共享 fixture。遵守 t.Setenv／t.Chdir 的并行限制；资源不能在父测试返回时先于并行子测试释放，按 t.Cleanup 与子测试完成顺序判断。
- 捕获 *testing.T 的 helper 绑定当前测试／子测试。Fatal／FailNow／SkipNow 在对应测试 goroutine 调用；工作 goroutine 的结果及失败须传回，并在测试结束前完成等待。并发用例以可控同步和有界等待建立完成证据，固定 sleep 不能证明完成。
- helper 提取或内联涉及 runtime.Caller／Callers、日志 caller skip 或 t.Helper 时，检查调用者身份、栈帧深度及失败归属是否参与契约；普通源码行号变化本身不构成缺陷。
- 循环捕获按模块／文件语言版本判断：Go 1.22 起循环声明的变量逐次创建，预声明后用 `=` 赋值仍会复用；检查实际捕获和修改时点。

## 输入与安全边界

按涉及的入口和数据流选择以下主题；同时核对部署、调用前提及已有防护，不把危险 API、缺少局部 guard 或固定配置值直接当成漏洞。

- **注入与路径**：从不可信输入追到 SQL、命令、模板等 sink。SQL 值参数化，动态标识符另查白名单；os/exec 直接 Command 不经 shell，shell 文本、可控程序或选项分别判断。HTML 输出核对上下文转义及可信类型绕过，[text/template](https://pkg.go.dev/text/template) 不提供 html/template 的自动转义。路径检查考虑平台、符号链接与 TOCTOU；Clean／字符串前缀不足以证明边界，识别目标版本支持的 os.Root 或已有等效实现。
- **身份与权限**：登录不等于资源授权，核对租户、资源归属和每个特权入口。令牌验签、允许算法、签发者／受众、有效期和重放防护按协议检查；不能信任客户端自报身份。涉及浏览器访问时，按认证方式核对 Cookie 属性、CSRF、CORS 与相关响应头，不机械套用到非浏览器服务。
- **随机数、加密与 TLS**：令牌、密钥等安全用途核对密码学随机源，不把普通业务随机一律替换为 crypto/rand。按用途核对成熟密码方案、认证完整性、nonce 约束与密钥管理。TLS 检查证书链、目标身份和自定义验证的真实效果；[InsecureSkipVerify](https://pkg.go.dev/crypto/tls#Config) 配合有效 VerifyConnection 等机制不自动构成漏洞，空回调或忽略验证错误也不能当作已有防护；核对会话恢复等适用路径。
- **出站请求与 SSRF**：可控 URL 追到实际连接目的地，核对 scheme、host／port、重定向各跳、DNS 解析与连接时的地址、代理和网络出口策略；仅检查 URL 格式或首次解析不能证明安全。区分明确可信目的地与任意外部 URL 的业务契约，不把合法内网调用一律禁止。按需查 [SSRF 边界](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)。
- **资源耗尽**：核对请求／响应体、解压后数据、批量规模、并发／队列和重试的有效上限及超时覆盖；Content-Length 或仅压缩前大小不足以限制实际读取。限制的 owner 可以是已证实有效的网关或调用方；流式、长连接按协议处理，不能统一套用固定超时或无条件缓存完整输入。
- **敏感信息**：检查程序是否把凭据、token、个人信息或内部错误写入日志、响应、追踪及调试端点，按接收者和数据分级判断脱敏与访问控制。审核报告只指出位置和影响，不复制秘密；示例占位符、公钥和非敏感标识不自动算凭据泄露。
- **外部写入**：超时不证明写入失败；重试、幂等、事务和恢复证据沿调用链核验，日志及错误不能把中间阶段当成最终成功。
- **依赖漏洞**：依赖变更、安全敏感路径或明确安全审核时，检查项目已有且版本固定的 [govulncheck](https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck) 等入口。记录可获取的工具版本、漏洞数据库来源／时点、Go 与依赖版本、构建条件和可达性证据；未报告可达调用不等于整体安全。缺少工具、所需的联网授权或适用环境时记验证缺口，不擅自安装最新版、升级依赖或声称扫描通过；执行遵守只读验证边界。

## 数值与性能

检查整数宽度、溢出、单位、舍入及金额／概率边界，浮点重排、随机调用及 map 遍历对结果的影响；计时器、重试或 Context 调整核对起算点、截止时间与已发生的外部效果。字符串与集合变换保留分隔符、尾随字符、nil／空及共享关系。性能结论须有实际负载、复杂度依据或同条件测量，区分外部 I/O 等待和进程内瓶颈；缓存需有权威数据与失效契约，池化或预分配本身不证明收益。

## 语义查证

按需查 [语言规范](https://go.dev/ref/spec)、[io](https://pkg.go.dev/io)、[bytes](https://pkg.go.dev/bytes)、[Context](https://pkg.go.dev/context)、[sync](https://pkg.go.dev/sync)、[errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)、[testing](https://pkg.go.dev/testing)、[Go modules](https://go.dev/ref/mod)、[cgo](https://pkg.go.dev/cmd/cgo) 与 [路径边界](https://go.dev/blog/osroot)。确认目标版本的语法及 API 支持；验证流程与授权见入口 SKILL。
