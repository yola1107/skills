# 编码与协议兼容

模块基线见[版本基线](version-baseline.md)。v3 区分普通 Go JSON 与 protobuf JSON；先固定外部协议再选 codec。

| 表示 | 包 | 需要核对的行为 |
| --- | --- | --- |
| Go JSON | `github.com/go-kratos/kratos/v3/encoding/json` | Go 字段/标签、数字、nil 与 omitempty |
| Protobuf JSON | `github.com/go-kratos/kratos/v3/encoding/protojson` | proto 字段名、int64、枚举、默认值与 well-known types |
| Protobuf 二进制 | `github.com/go-kratos/kratos/v3/encoding/proto` | 字段号与消息兼容 |

`Content-Type` 与 `Accept` 选择的 codec 必须已注册。保留普通 JSON 媒体类型但需要 protobuf JSON 语义时，通过明确的 decoder/encoder 适配；核对客户端 header 和错误响应，不能只凭 import 判断线上编码。

## 自定义编码

自定义 codec 实现 `encoding.Codec` 的 `Marshal(any) ([]byte, error)`、`Unmarshal([]byte, any) error`、`Name() string`。注册是进程级行为，相同名字会影响所有使用方，避免依赖隐含导入顺序。

HTTP 可用 `RequestDecoder`、`ResponseEncoder`、`ErrorEncoder` 保留特殊协议。签名、hash、冻结快照需要原始 bytes 时保存或透传原文，重新编码后的同义 JSON 不等于同一证据。

## 路径与表单

手写 HTTP 入口使用 `http.Context` 的绑定函数，客户端构建路径可用 `http.BuildPath`。生成 handler 已完成的绑定不应在 service 再做一次。

涉及 BuildPath、FieldMask 或 Timestamp 时先查[正式版与主干差异](version-baseline.md#正式版与主干差异)。采用路径转义修复的版本后，向 BuildPath 传入原始值：预转义的 `a%2Fb` 会变成 `a%252Fb`；普通变量或 `*` 将斜线作为段内字符转义，资源模板中的层级分隔符按模板保留。

核对 Proto 名与 JSON 名、具名 body 的 query 排除、路径保留字符及已有签名样本。表单编码还需确认输入对象不被修改，并在实际时区下验证 Timestamp 往返；使用修复前版本时保留相应兼容处理，升级后重新核对，避免重复转义或重复补偿。

## 验证

固定样本至少覆盖实际协议中的金额和 int64、空集合/null、默认字段、枚举、错误正文，以及未知字段策略。对于流式响应，同时核对消息 framing 与关闭行为。

来源：[编码文档](https://go-kratos.dev/zh-cn/docs/component/encoding/)、[HTTP 绑定](https://go-kratos.dev/zh-cn/docs/component/transport/http/)。
