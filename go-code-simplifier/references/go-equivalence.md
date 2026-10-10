# Go 等价边界

仅阅读候选相关的小节。以下是转换时须核对的语义；判断以实际实现、调用契约和目标版本为准，编译或工具诊断不能独立证明等价。

## 符号、类型与版本

- 改名确认符号身份、作用域、遮蔽、闭包与全部引用，优先可用的 gopls 等语义工具；文本或 AST 名称匹配不等于符号匹配。接口参数和结果名称可清理，类型、数量、顺序及可变参数约定保持不变。
- 保持公开 API、接收者类型、方法集、类型别名身份；补查 tag、模板、反射、字符串注册、生成源和构建变体。仓内无调用方或工具未找到引用，不足以删除公开符号或外部契约。
- 保持具体类型、整数宽度、溢出、常量值及有类型／无类型属性；核对 typed nil 到 interface 的转换。工具链较新不代表能提高最低 Go 版本，工具建议逐项检查。
- import 别名按实际包名与消歧需要判断，路径末段不同本身不要求别名。删除导入前确认包初始化、传递依赖和注册副作用，保留必要的空白导入。
- [cgo 前导注释](https://pkg.go.dev/cmd/cgo#hdr-Using_cgo_with_the_go_command) 是构建输入，保留其与 `import "C"` 的直接关联及其中的 C 声明、`#cgo` 配置；不能按废弃代码注释删除。禁用 cgo 的检查不覆盖这些文件。

## 求值、返回与存储

- 保持求值次数、顺序、条件执行和短路，以及时间、随机调用、浮点分组、NaN／正负零语义。移动变量须核对快照时点和跨迭代状态。
- 未读结果或无读取的私有字段不代表求值可删：核对共享状态写入、外部调用、类型断言、索引及 nil 访问的 panic。可重算的值仍可能是快照、缓存或恢复证据。
- 直返保持类型与转换、错误身份／链／优先级、失败部分值及 defer 对结果或局部变量的读写；删除包装前保留错误转换、事务、同步和收尾职责。修改对外错误或日志文本，新增错误传播、错误包装、日志、重试、校验或 recover，均按行为变化处理。

下面失败时丢弃部分值，不能直接替换为 `return load()`：

```go
value, err := load()
if err != nil {
	return 0, err
}
return value, nil
```

下面 defer 读取局部 err，最后两行不能直接替换为 `return work()`：

```go
func execute() error {
	var err error
	defer func() { record(err) }()
	err = work()
	return err
}
```

## 集合、字段与共享

- 保持 nil／零值／已分配空集合、map 缺失与零值、slice 长度与容量、顺序和重复项，尤其是序列化差异。
- 保持别名和所有权，副本与原对象不能任意互换；核对已使用的锁及其他不可复制值。
- 拆分字段或改为具名初始化时，保留字段顺序、类型、tag、嵌入关系及各值的求值顺序。

## 控制流、同步与函数边界

- 重排 guard、命名条件或合并分支时，确认默认赋值、if-init 作用域、短路及互斥关系。`continue`／`break`／`return` 保持退出目标，核对循环尾部、post、label、switch 和 select。
- 保持锁范围、顺序及锁内调用，取消、goroutine／channel 生命周期、收发与背压，以及资源创建、回滚和关闭时点。
- defer 调用登记时求值，闭包可能执行时读取；保持捕获、执行顺序和 panic／recover。循环体移入 helper 可能提前解锁或关闭资源，recover 也须保持与延迟函数的直接调用关系。
- 提取、内联或合并逻辑逐调用点核对输入、失败、求值及业务契约，保留指令和注释的作用位置。
- 涉及 [runtime.Caller／Callers](https://pkg.go.dev/runtime#Caller)、日志 caller skip 或 [testing.T.Helper](https://pkg.go.dev/testing#T.Helper) 时，核对提取和内联对调用者身份、栈帧深度及测试归属的影响。不要求普通格式清理保持所有源码行号；但明确依赖 caller、堆栈或位置的契约不能忽略。

## unsafe 与跨语言边界

涉及 [unsafe.Pointer](https://pkg.go.dev/unsafe#Pointer)／uintptr、系统调用或零拷贝视图时，核对目标版本允许的转换形式、对象范围、对齐／布局、别名、不可变性和 GC 存活。uintptr 是整数，不是维持对象存活的引用；不能把规范要求的同一表达式或调用参数内转换拆为普通中间变量。保留 [runtime.KeepAlive](https://pkg.go.dev/runtime#KeepAlive) 等生命周期约束，但不能用它为本来不合法的转换补救。能证明等价时可改用普通索引等安全写法，不为保留 unsafe 而保留。

例如，p 非 nil 且结果仍在原分配对象内的指针算术，不能这样拆分：

```go
// 先核对对象范围等前提。
next := unsafe.Pointer(uintptr(p) + offset)
```

```go
// 非等价候选：uintptr 被存入变量后再转回指针。
addr := uintptr(p)
next := unsafe.Pointer(addr + offset)
```

涉及 cgo 时还须核对 [Go/C 指针传递与保留](https://pkg.go.dev/cmd/cgo#hdr-Passing_pointers)、pinning、分配与释放 owner；保留前导注释只是构建约束。不因 vet、race、checkptr 或单次运行通过便认定转换有效。

## 测试契约

清理测试保留输入、断言、失败／跳过条件、setup／cleanup、同步及 Example 输出注释。验证范围按入口的实际转换规则选择；补测针对尚未闭合的契约，不要求补齐原函数的全部覆盖。测试设施不扩大生产 API 或增设生产全局开关，覆盖率、跳过用例或交叉编译不代表路径已实际执行。
