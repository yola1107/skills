# CLI 与代码生成

核心与工具的版本关系见[版本基线](version-baseline.md)。涉及生成或工具准备时，核对相关 Makefile/Buf 配置、go:generate 与文件头；沿用项目命令和未变化的核验结果。

## 工具路径

以下是 Kratos v3 的独立命令模块：

```text
github.com/go-kratos/kratos/cmd/kratos/v3
github.com/go-kratos/kratos/cmd/protoc-gen-go-http/v3
github.com/go-kratos/kratos/cmd/protoc-gen-go-errors/v3
```

只有任务需要准备工具时才安装。下面的变量应填入已经核实的各工具版本，不能推断它们都与核心 tag 相同：

```sh
go install github.com/go-kratos/kratos/cmd/kratos/v3@${KRATOS_CLI_VERSION:?set reviewed CLI version}
go install github.com/go-kratos/kratos/cmd/protoc-gen-go-http/v3@${KRATOS_HTTP_VERSION:?set reviewed HTTP generator version}
go install github.com/go-kratos/kratos/cmd/protoc-gen-go-errors/v3@${KRATOS_ERRORS_VERSION:?set reviewed error generator version}
```

Protobuf、gRPC、Wire、OpenAPI 和校验工具使用各自的 module 与固定版本。确保实际执行的二进制和项目声明一致，避免 PATH 中旧工具生成不匹配的 import。

## 命令选择

- `kratos new` 用于获准创建的新项目；模板来源与 revision 需要符合目标版本。已有单 module 应用通常在原仓内扩展。
- `kratos proto client`、`kratos proto server` 的参数按已安装 CLI 的 `--help` 核对；已有实现不能被生成 service stub 覆盖。
- 运行与生成优先使用仓库命令，例如已有的 `make api`、`make generate`；这些名称并非每个项目都存在。
- Wire 修改输入后重生成；Proto 修改后检查全部受影响的生成代码与调用方。

生成后验证本次受影响的行为与调用方，记录工具版本和检查结果；检查范围与环境见[交付复核](../best-practices/overview.md)。

来源：[官方 CLI](https://go-kratos.dev/zh-cn/docs/getting-started/usage/)、[v3 工具迁移](https://go-kratos.dev/zh-cn/docs/migration/v2-to-v3/)。
