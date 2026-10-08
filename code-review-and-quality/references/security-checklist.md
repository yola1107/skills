# 安全检查清单

本技能的安全审核参考。按实际攻击面和技术栈选择章节；浏览器设置、数值示例和安装流程不是所有项目的统一要求。提出修改前先检查已有防护。本文件可独立使用，无需其他技能。

## 目录

- [威胁建模（从这里开始）](#威胁建模从这里开始)
- [提交前检查](#提交前检查)
- [身份认证](#身份认证)
- [权限校验](#权限校验)
- [输入校验](#输入校验)
- [安全响应头](#安全响应头)
- [CORS 配置](#cors-配置)
- [数据保护](#数据保护)
- [依赖安全](#依赖安全)
  - [Go 模块](#go-模块)
  - [JavaScript 包管理器](#javascript-包管理器)
- [AI / LLM 安全](#ai--llm-安全)
- [错误处理](#错误处理)
- [OWASP Top 10 速查](#owasp-top-10-速查)
- [OWASP LLM Top 10 速查](#owasp-llm-top-10-速查)

## 威胁建模（从这里开始）

选择防护措施前，先花五分钟从攻击者角度检查：

- [ ] 标出信任边界：请求、上传、webhook、第三方 API、LLM 输出，以及不受控进程写入的本地数据
- [ ] 明确保护对象：凭据、个人信息、支付数据、管理操作和资金流转
- [ ] 对每个边界检查 STRIDE：身份伪造、篡改、抵赖、信息泄漏、拒绝服务和权限提升
- [ ] 在正常用例旁补充滥用场景：“攻击者会怎样利用它？”

## 提交前检查

- [ ] 检查暂存变更中的秘密，只报告位置或脱敏内容，不把原始值打印到工具输出或审核报告
- [ ] `.gitignore` 覆盖 `.env`、`.env.local`、`*.pem`、`*.key`
- [ ] `.env.example` 使用占位值，不包含真实秘密

## 身份认证

- [ ] 密码使用 bcrypt（成本参数 ≥12）、scrypt 或 argon2 哈希
- [ ] 会话 cookie 设置 `httpOnly`、`secure`、`sameSite: 'lax'`
- [ ] 配置合理的会话过期时间
- [ ] 登录限流符合已记录的滥用模型和部署方式；多实例使用预期的共享限额，避免按进程叠加
- [ ] 密码重置 token 有明确且有界的有效期，并且只能使用一次
- [ ] 连续失败后锁定账号并通知用户（可选）
- [ ] 敏感操作支持 MFA（可选，但建议支持）

## 权限校验

- [ ] 每个受保护接口都检查身份认证
- [ ] 每次资源访问都核对归属或角色，防止 IDOR
- [ ] 管理接口验证管理角色
- [ ] API key 权限限制在必要范围
- [ ] JWT 校验签名、有效期和签发方
- [ ] 资源与租户身份来自已授权的服务端状态；有效登录或请求提供的 ID 本身不证明资源归属

## 输入校验

- [ ] 用户输入在 API 路由、表单处理等系统边界校验
- [ ] 使用白名单校验，而非仅依赖黑名单
- [ ] 限制字符串的最小和最大长度
- [ ] 校验数值范围
- [ ] 使用适当的库校验邮箱、URL 和日期格式
- [ ] 文件上传限制类型和大小，并验证实际内容
- [ ] SQL 值参数化，不拼接输入
- [ ] HTML 输出编码，优先使用框架自动转义
- [ ] 重定向前校验 URL，防止开放重定向
- [ ] 服务端 URL 请求使用白名单，阻止访问私有或保留 IP，防止 SSRF
- [ ] 删除、移动、覆盖等路径操作，执行前解析符号链接，检查允许的根目录、最小深度及所有权证据

### 破坏性路径操作

目标路径来自数据时，先解析并检查范围。解析结果只是待核验的候选，不能代替授权：

```typescript
import { realpath, readFile } from 'node:fs/promises';
import { resolve, relative, isAbsolute, join, sep } from 'node:path';

const ALLOWED_ROOTS = ['/var/lib/myapp/sessions']; // 使用明确白名单，不是路径模式
const MIN_DEPTH = 1;                               // 确保根目录本身不会成为目标

async function resolveDeletable(candidate: string, expectedOwner: string) {
  const target = await realpath(resolve(candidate)); // 检查之前解析符号链接
  const inRoot = ALLOWED_ROOTS.some((root) => {
    const rel = relative(root, target);
    // 仅拒绝 `rel === '..'` 和 `'../'`；直接使用 `startsWith('..')`
    // 还会错误拒绝名为 `..cache` 的合法子目录。
    if (rel === '' || rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) return false;
    return rel.split(sep).length >= MIN_DEPTH;
  });
  if (!inRoot) throw new Error(`refusing: outside allowed roots (${target})`);

  const owner = await readFile(join(target, '.owner'), 'utf8').catch(() => null);
  if (owner?.trim() !== expectedOwner) throw new Error(`refusing: unproven owner (${target})`);
  return target;
}
```

复制此示例时，必须同时说明它没有解决的限制：

- **标记文件只能自证。** 能在根目录内写入的进程也能写入 `.owner`。`expectedOwner` 必须来自认证后的状态，标记还需有完整性保护，例如受限制的文件归属或 MAC，才能用作授权依据；否则它只是针对错误目标的一致性检查。
- **返回路径仍存在检查与使用之间的竞态。** 不可信进程可能在检查后、操作前替换祖先目录。此时应使用具有禁止跟随符号链接、限制在根目录之下等语义的描述符操作，或保证操作期间目录层级不可变。

## 安全响应头

```
Content-Security-Policy: default-src 'self'; script-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0  （禁用，依赖 CSP）
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## CORS 配置

```typescript
// 限制明确来源的配置（推荐）
cors({
  origin: ['https://yourdomain.com', 'https://app.yourdomain.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
})

// 通配来源仅适用于明确公开、且不携带凭据的资源。
// 它不能代替权限校验。
cors({ origin: '*' })
```

## 数据保护

- [ ] API 响应排除 `passwordHash`、`resetToken` 等敏感字段
- [ ] 不记录密码、token、完整信用卡号等敏感数据
- [ ] 法规要求时，对静态存储的个人信息加密
- [ ] 外部通信使用 HTTPS
- [ ] 数据库备份加密
- [ ] 个人数据分类管理，按明确目的采集，并最小化收集范围
- [ ] 个人数据有保存期限及可执行的删除路径，覆盖备份、缓存和索引
- [ ] 需要时支持数据主体的导出/删除请求；向第三方共享数据有相应同意和数据处理协议

## 依赖安全

### Go 模块

- 确认所属 go.mod、支持的工具链、实际构建标签/平台及已有 go.work。独立模块分别处理，不为审核添加工作区文件或 replace 指令。
- 核对 go.mod 和解析后的模块图，检查版本选择、直接与传递依赖变化、替换项和本地 fork。go.sum 记录完整性校验值，不负责选择依赖版本。
- 依赖变化时检查发布/迁移说明和受影响 API。依赖或安全任务确有需要时，使用仓库固定版本的漏洞检查入口，并在实际构建配置下判断可达性。可选工具缺失应说明，不自动安装或升级。
- 使用项目已有 Go 工具检查可获得的模块完整性证据。获准实施并修改 go.mod/go.sum 时，遵循项目的 tidy-diff 和 verify 要求；只读审核不重写这些文件。
- Go 请求处理需要沿真实路由确认错误和权限检查，包括中间件、RPC 适配和后台入口。SQL 值参数化，动态标识符需校验；Go 类型本身不能证明资源归属或 SQL 构造安全。

### JavaScript 包管理器

先定位**安装边界**。包受上级 `workspaces` 声明管理时，使用该工作区根目录；否则使用同时拥有依赖清单与依赖图的最近项目根目录。在该边界核对 `packageManager`（若存在）、锁文件和 CI 命令。三者冲突或存在相互竞争的包管理器锁文件时，停止相关安装操作。嵌套项目只有不属于上级工作区时才独立，独立子项目可以使用不同包管理器。

| 包管理器/版本线索 | CI 固定依赖安装 | 已知漏洞通告检查 |
|---|---|---|
| npm（`package-lock.json` 或 `npm-shrinkwrap.json`） | `npm ci` | `npm audit` |
| pnpm | `pnpm install --frozen-lockfile` | `pnpm audit` |
| Yarn 2+ | `yarn install --immutable` | `yarn npm audit -A -R` |
| Yarn 1 | `yarn install --frozen-lockfile` | `yarn audit` |

未列出的包管理器或版本应查其官方文档，不套用其他包管理器的命令或更新版本的默认值。

### 安装脚本控制

这些步骤仅适用于已授权的依赖安装或修改任务。审核时检查策略和证据，不执行安装或创建提交。使用项目固定的工具版本。

未确认客户端默认行为时，不先执行普通安装来“发现”依赖生命周期脚本。

1. 首次安装时禁用依赖脚本，或使用已说明的默认拒绝、失败即阻止执行的策略。
2. 批准前检查准确的脚本源码和包版本。
3. 在安装边界记录最小范围的原生允许/拒绝策略，并提交。
4. 使用该策略完成干净、固定依赖的安装，验证所需包仍能构建。

**特定时间点的记录：** 包管理器默认值和命令变化较快。使用下表前，应根据项目固定版本对应的官方文档核验。

| 包管理器版本 | 原生策略 |
|---|---|
| 未核验细粒度审批能力的 npm | 先使用 `npm ci --ignore-scripts`；需要项目级禁用时持久设置 `ignore-scripts=true`。在允许已审核的依赖脚本前，保持禁用，或明确升级到满足要求的版本。 |
| npm 11.18.x（已核验 11.18.0） | 默认会执行未审核的依赖脚本并给出警告。普通安装前设置 `strict-allow-scripts=true`，再从安装边界运行不感知 workspace 的 `npm install-scripts ls`；批准固定到版本，拒绝覆盖整个包名。 |
| npm 12.x（已核验 12.0.1） | 默认跳过未审核的依赖脚本；`strict-allow-scripts=true` 会在执行安装前因这些脚本而失败。使用相同的 `npm install-scripts` 审核和批准流程。 |
| pnpm 11+ | 使用 `pnpm approve-builds`，提交 `allowBuilds` 决策；`strictDepBuilds` 默认是 `true`，未审核的构建会失败。 |
| pnpm 10.26–10.x | 明确配置 `allowBuilds`，或使用 `pnpm approve-builds` 配合旧的 `onlyBuiltDependencies` / `ignoredBuiltDependencies` 列表。设置 `strictDepBuilds: true`，v10 默认值为 `false`。 |
| pnpm 10.1–10.25 | `pnpm approve-builds` 记录旧列表；支持时启用 `strictDepBuilds`（10.3+）。 |
| 更旧或未知的 pnpm | 先运行 `pnpm install --frozen-lockfile --ignore-scripts`。除非固定版本的文档提供可强制执行的策略，否则继续禁用脚本。 |
| Yarn 4.14+ | 默认禁用依赖的 postinstall；仅通过顶层 `dependenciesMeta.<package>.built: true` 允许必要例外。 |
| Yarn 2–4.13 | 在 `.yarnrc.yml` 中设置 `enableScripts: false`，再通过顶层 `dependenciesMeta.<package>.built: true` 允许必要例外；不全局开启脚本。 |
| Yarn 1 | 先运行 `yarn install --ignore-scripts`；除非按固定版本的文档流程审核了每个例外，否则继续禁用脚本。 |

核验依据：[npm install-scripts](https://docs.npmjs.com/cli/v11/commands/npm-install-scripts/)、[npm 安装策略](https://docs.npmjs.com/cli/v11/commands/npm-install/)和 [CLI 发布记录](https://github.com/npm/cli/releases)；[pnpm approve-builds](https://pnpm.io/cli/approve-builds) 和[构建设置](https://pnpm.io/settings#allowbuilds)；[Yarn 安全说明](https://yarnpkg.com/features/security)和[依赖清单设置](https://yarnpkg.com/configuration/manifest#dependenciesMeta)。

**供应链检查**（漏洞通告扫描无法识别刚出现的恶意包）：

- [ ] 每个项目/工作区根目录仅有一份权威锁文件，已提交且 CI 不重写
- [ ] 严重/高危发现按可达性分类，延期有理由和复核日期
- [ ] 不自动执行 `npm audit fix --force` 等强制修复；检查修复 diff 和变更记录
- [ ] 包管理器支持时，核验注册源签名和来源证明
- [ ] 依赖生命周期脚本在首次执行前被阻止，批准仅通过固定版本包管理器的原生策略
- [ ] 新依赖检查归属、维护状态、发布时长、来源、传递依赖和近似名称欺骗

## AI / LLM 安全

适用于调用 LLM 的聊天机器人、摘要、Agent、RAG 等功能：

- [ ] 模型输出按不可信输入处理，不直接进入 `eval`、SQL、shell、`innerHTML` 或文件路径
- [ ] 假设提示注入可能发生，在代码中执行权限限制，不依赖系统提示词
- [ ] 秘密、其他租户的数据和完整系统提示词不进入上下文
- [ ] 工具/Agent 权限有明确范围，破坏性或不可逆操作需要确认
- [ ] 限制 token、请求频率和递归/循环深度，控制资源消耗

## 错误处理

```typescript
// 生产环境：返回通用错误，不暴露内部细节
res.status(500).json({
  error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' }
});

// 生产环境不可采用：
res.status(500).json({
  error: err.message,
  stack: err.stack,         // 泄漏内部堆栈
  query: err.sql,           // 泄漏数据库细节
});
```

## OWASP Top 10 速查

| 编号 | 漏洞类别 | 防范方式 |
|---|---|---|
| 1 | 访问控制失效 | 每个接口检查认证/权限，校验资源归属 |
| 2 | 加密机制失效 | HTTPS、强哈希、代码中不存秘密 |
| 3 | 注入 | 查询参数化、输入校验 |
| 4 | 不安全设计 | 威胁建模、先明确需求契约 |
| 5 | 安全配置错误 | 安全响应头、最小权限、依赖检查 |
| 6 | 存在漏洞的组件 | 使用对应生态的依赖检查（`npm audit`、`pip-audit` 等），维护依赖版本，减少不必要依赖 |
| 7 | 身份认证失效 | 强密码、限流、会话管理 |
| 8 | 数据完整性失效 | 验证更新和依赖，使用签名产物 |
| 9 | 日志机制失效 | 记录安全事件，不记录秘密 |
| 10 | SSRF | 校验 URL 和白名单，限制出站请求 |

## OWASP LLM Top 10 速查

适用于具有 LLM 功能的应用。参考 [OWASP GenAI 安全项目](https://genai.owasp.org/llm-top-10/)。

| ID | 风险 | 防范方式 |
|---|---|---|
| LLM01 | 提示注入 | 不把系统提示词当安全边界，在代码中执行权限限制 |
| LLM02 | 敏感信息泄漏 | 秘密和个人信息不进入提示，过滤输出 |
| LLM03 | 供应链 | 像审核依赖一样审核模型、数据集和插件 |
| LLM04 | 数据与模型投毒 | 使用可信模型来源、验证完整性，审核微调和 RAG 数据 |
| LLM05 | 输出处理不当 | 输出按不可信输入处理，校验、参数化并编码 |
| LLM06 | 过度授权 | 限制工具权限，确认破坏性操作 |
| LLM07 | 系统提示词泄漏 | 假设系统提示词可能泄漏，不在其中存放秘密 |
| LLM08 | 向量与嵌入风险 | 按租户隔离 RAG 嵌入，索引前校验文档 |
| LLM09 | 错误信息 | 用来源支持回答，核验关键结论，保留人工参与 |
| LLM10 | 无界资源消耗 | 限制 token、请求频率和循环/递归深度 |
