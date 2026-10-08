---
name: code-simplification
description: 在保持行为不变的前提下简化代码，提高可读性。用于代码能够正常工作，但阅读、维护或扩展成本偏高的情况，以及审核和重构积累了不必要复杂度的代码。
---

# 代码简化

> 受 [Claude Code Simplifier 插件](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md)启发。本技能将其改编为不限定模型、按流程执行的通用技能，适用于各类 AI 编码助手。

## 概述

通过降低复杂度来简化代码，同时完整保持行为。目标是让代码更容易阅读、理解、修改和调试。每项简化都应回答一个问题：“新加入的成员能否比以前更快理解这段代码？”

修改前阅读适用的项目规则并检查当前工作区。审核请求保持只读；简化请求授权的是指定范围内的本地清理，不包含无关修复、提交或发布。处理 Go 代码时，结合下述原则和本技能内的 [Go 行为等价简化](references/go-simplification.md)参考文档。

## 适用场景

- 功能已经正常工作、测试通过，但实现显得过于繁重
- 代码审核发现可读性或复杂度问题
- 遇到深层嵌套、长函数或含义不清的命名
- 重构在时间压力下写出的代码
- 整理分散在多个文件中的相关逻辑
- 合并改动后出现重复实现或不一致

**不适用的情况：**

- 代码已经清晰易读，没有具体简化收益
- 尚未理解代码行为，需要先补充上下文
- 代码处于性能关键路径，且“简化”版本经测量明显更慢
- 即将完整重写模块，此时清理将被丢弃的实现没有收益

## 五项原则

### 1. 完整保持行为

只改变行为的表达方式，所有输入、输出、副作用、错误行为和边界情况都必须保持一致。无法确认等价时，不实施该项简化。

```
每次修改前自检：
→ 对每种输入，输出是否相同？
→ 错误行为是否保持？
→ 副作用及其顺序是否保持？
→ 完成必要的符号或导入同步后，测试是否保持原有行为断言并继续通过？
```

### 2. 遵循项目约定

简化应提高代码与项目的一致性。开始前：

```
1. 阅读适用的 AGENTS.md、CLAUDE.md 和项目约定
2. 查看相邻代码如何处理类似情况
3. 遵循项目在以下方面的风格：
   - 导入顺序和模块组织
   - 函数声明方式
   - 命名约定
   - 错误处理方式
   - 类型注解的详细程度
```

破坏项目一致性的改写只会增加维护成本。

### 3. 清晰优先于巧妙

如果紧凑写法需要读者停下来推演，优先使用更直接的表达。

```typescript
// 不清晰：密集的三元表达式链
const label = isNew ? 'New' : isUpdated ? 'Updated' : isArchived ? 'Archived' : 'Active';

// 清晰：容易阅读的状态映射
function getStatusLabel(item: Item): string {
  if (item.isNew) return 'New';
  if (item.isUpdated) return 'Updated';
  if (item.isArchived) return 'Archived';
  return 'Active';
}
```

```typescript
// 不清晰：reduce 中内嵌了多层处理逻辑
const result = items.reduce((acc, item) => ({
  ...acc,
  [item.id]: { ...acc[item.id], count: (acc[item.id]?.count ?? 0) + 1 }
}), {});

// 清晰：为归约步骤命名，保持相同的对象和值结构
function countItem(acc: Record<string, { count: number }>, item: Item) {
  return {
    ...acc,
    [item.id]: {
      ...acc[item.id],
      count: (acc[item.id]?.count ?? 0) + 1,
    },
  };
}
const result = items.reduce(countItem, {});
```

### 4. 保持适度

简化也可能过度，需要避免：

- **过度内联**：删除原本用于命名业务概念的 helper，反而让调用处更难读
- **合并无关逻辑**：把两个简单函数合成一个复杂函数，未必带来简化
- **删除有意义的抽象**：保留当前职责、所有权边界或已有扩展点；假设中的未来用途或 mock 便利，本身不足以支持新增或保留一层
- **只追求行数**：判断标准是理解是否更容易

### 5. 遵守清理范围

默认关注最近修改的代码。用户指定文件或目录时，检查该完整范围，包括相关测试。避免顺手重构无关代码。保留用户现有改动，生成代码通过源或生成器更新，不直接手改。

## 简化流程

### 第一步：先理解再修改（切斯特顿围栏）

修改或删除之前，先弄清楚代码为什么存在。切斯特顿围栏原则是：看到一道围栏却不理解其用途时，不要先拆掉它。先确定原因，再判断原因是否仍然成立。

```
简化前回答：
- 这段代码承担什么职责？
- 谁调用它？它调用谁？
- 有哪些边界情况和错误路径？
- 是否有测试说明预期行为？
- 为什么采用当前写法？是否涉及性能、平台限制或历史原因？
- 如果原因仍不明确，查看 Git 历史；没有历史记录，不妨碍依据当前代码和契约得出结论。
```

尚不能回答这些问题时，先阅读更多上下文。

### 第二步：识别简化机会

将以下模式作为候选，随后确认具体阅读收益和等价性要求。次数、嵌套和长度只是定位线索，不直接要求修改。

**结构复杂度：**

| 模式 | 信号 | 可选简化 |
|---------|--------|----------------|
| 深层嵌套 | 主流程被遮蔽 | 利用已有退出条件形成 guard，或提取完整职责，保持作用域与求值语义 |
| 长函数 | 混合不同职责，或需要反复跳转阅读 | 仅在有意义的命名边界能改善理解时拆分，长度本身不是理由 |
| 嵌套三元表达式 | 需要记住多层条件才能理解 | 改为 if/else、switch 或查找对象 |
| 布尔参数开关 | 调用处看不出选择了哪种行为 | 先明确契约；options 对象或独立函数是可选方案，不自动替换 |
| 重复条件 | 同一业务决策在多处维护 | 仅在输入、失败和演化契约一致时共享 |

**命名与可读性：**

| 模式 | 信号 | 可选简化 |
|---------|--------|----------------|
| 含糊名称 | 实际使用处看不清角色 | 选择能够区分角色的名称，不重复显然的上下文 |
| 难懂缩写 | 需要猜测拼写含义 | 在有帮助时展开；保留作用域内清楚的 `ctx`、`err`、`cfg` 等惯用名称 |
| 误导性名称 | 名为 `get` 的函数还修改状态 | 使名称反映实际行为 |
| 复述“做什么”的注释 | 在 `count++` 上方写 `// 计数加一` | 代码已经清楚时删除这类注释 |
| 解释“为什么”的注释 | `// API 在负载较高时不稳定，因此需要重试` | 保留代码本身无法表达的原因 |

**冗余：**

| 模式 | 信号 | 可选简化 |
|---------|--------|----------------|
| 重复逻辑 | 同一规则或职责存在于多处 | 比较契约后在负责方集中维护，不能仅凭行文相似合并 |
| 死代码 | 不可达分支、未使用变量、被注释掉的实现 | 确认确实无用后删除 |
| 多余抽象 | 包装没有提供额外价值 | 内联包装，直接调用实际实现 |
| 过度设计 | 多层工厂、只有一种策略的策略框架 | 改为简单直接的实现 |
| 冗余类型断言 | 对已经推导出的类型再次断言 | 删除冗余断言 |

### 第三步：分批实施

按职责连贯、便于审核的批次修改，并在有意义的批次完成后验证受影响行为。无关清理分开处理；任务必需的准备和调用方适配可以一起完成。本技能不强制拆分提交或 PR。

```
每个相关批次：
1. 完成范围内改动，复审受影响的完整函数
2. 通过项目已有入口运行相关检查
3. 复用有效结果，直到新改动、失败或具体风险需要追加检查
4. 分类失败，只修正或撤销本轮改动，保留用户工作
```

批次应足够小，能够定位回归来自哪项改动。有依赖的修改一起完成，不因每次改名或格式调整重复运行全套测试。提交或发布必须已有对应授权。

**按需自动化：** 重复变换确实值得自动化时，使用已有语义或 AST 工具。预览选中的符号和编辑范围；文本替换不能证明符号身份相同。不因 diff 超过某个行数就创建自动化框架或安装工具。

### 第四步：验证结果

所有简化完成后，从整体比较：

```
对照修改前后：
- 是否确实更容易理解？
- 是否引入了不符合现有代码约定的新模式？
- diff 是否清晰、便于审核？
- 团队成员是否会认为整体质量有所提高？
```

若修改后更难理解，或无法证明等价，只撤销对应的本轮改动。保留用户工作，记录具体原因，继续处理其他已经能够确认的改进。

## 各语言专项说明

### Go

阅读 [Go 行为等价简化](references/go-simplification.md)，核对命名、guard、直返、nil/interface、数据共享、锁、defer、模块与验证。该参考包含具体示例和等价性要求，不依赖其他技能。

### TypeScript / JavaScript

以下是候选写法。应用前检查属性读取副作用、集合语义，以及错误和时序契约，不能当作通用替换规则。

```typescript
// 有条件适用：删除 async 包装前需要核对契约
// 修改前
async function getUser(id: string): Promise<User> {
  return await userService.findById(id);
}
// 仅在 findById 不会同步抛错，且调用方不观察 Promise 身份、
// 调度或异步堆栈行为时，才可使用下面的写法。
// 否则保留 async 包装，它会将同步异常转换成 Promise 拒绝。
function getUser(id: string): Promise<User> {
  return userService.findById(id);
}

// 简化：冗长的条件赋值
// 修改前
let displayName: string;
if (user.nickname) {
  displayName = user.nickname;
} else {
  displayName = user.fullName;
}
// 修改后
const displayName = user.nickname || user.fullName;

// 简化：为标准稠密数组手动构建筛选结果
// 修改前
const activeUsers: User[] = [];
for (const user of users) {
  if (user.isActive) {
    activeUsers.push(user);
  }
}
// 修改后
const activeUsers = users.filter((user) => user.isActive);

// 简化：冗余的布尔返回
// 修改前
function isValid(input: string): boolean {
  if (input.length > 0 && input.length < 100) {
    return true;
  }
  return false;
}
// 修改后
function isValid(input: string): boolean {
  return input.length > 0 && input.length < 100;
}
```

### Python

```python
# 简化：冗长的字典构建
# 修改前
result = {}
for item in items:
    result[item.id] = item.name
# 修改后
result = {item.id: item.name for item in items}

# 简化：用提前返回展开嵌套条件
# 修改前
def process(data):
    if data is not None:
        if data.is_valid():
            if data.has_permission():
                return do_work(data)
            else:
                raise PermissionError("No permission")
        else:
            raise ValueError("Invalid data")
    else:
        raise TypeError("Data is None")
# 修改后
def process(data):
    if data is None:
        raise TypeError("Data is None")
    if not data.is_valid():
        raise ValueError("Invalid data")
    if not data.has_permission():
        raise PermissionError("No permission")
    return do_work(data)
```

### React / JSX

```tsx
// 简化：冗长的条件渲染
// 修改前
function UserBadge({ user }: Props) {
  if (user.isAdmin) {
    return <Badge variant="admin">Admin</Badge>;
  } else {
    return <Badge variant="default">User</Badge>;
  }
}
// 修改后
function UserBadge({ user }: Props) {
  const isAdmin = user.isAdmin;
  const variant = isAdmin ? 'admin' : 'default';
  const label = isAdmin ? 'Admin' : 'User';
  return <Badge variant={variant}>{label}</Badge>;
}

// 简化候选：通过中间组件逐层传递 props
// 修改前先判断 context 或组合是否更合适。
// 这里需要结合设计判断，先报告问题，不自动重构。
```

## 常见借口与判断

| 借口 | 判断 |
|---|---|
| “能运行就不用动” | 难读的代码在出现故障时也难修；有效简化能降低后续每次修改的成本。 |
| “行数越少越简单” | 一行嵌套三元表达式未必比五行 if/else 简单，应比较理解成本。 |
| “顺手把无关代码也清理一下” | 范围外清理会增加 diff 噪声，并可能引入原本不涉及的回归。 |
| “类型已经说明一切” | 类型表达结构，命名还需要表达意图；好名字能说明签名之外的职责。 |
| “这个抽象以后可能有用” | 当前没有用途的假设性抽象会增加复杂度，确有需要时再引入。 |
| “原作者肯定有原因” | 先通过历史和上下文确认原因；有些复杂度也只是多次迭代留下的结果。 |
| “新增功能时顺便重构” | 无关清理分开；只有属于任务范围、且使改动完整可验证的必要准备才一起实施。 |

## 需要警惕的情况

- 必须削弱断言或改变预期行为才能让简化通过测试；机械同步符号和导入不属于此类
- “简化”后代码更长且更难理解
- 为迎合个人偏好改名，偏离项目约定
- 以“代码更干净”为由删除错误处理
- 简化尚未理解的代码
- 将多项简化合成难以审核的大提交
- 未经要求重构任务范围之外的代码

## 验证

一次简化完成后，确认：

- [ ] 受影响测试通过，输入、断言含义、失败/跳过条件、setup/cleanup 和同步语义保持；允许必要的符号和导入同步
- [ ] 构建成功，没有新增警告
- [ ] lint 和格式检查通过，没有风格回退
- [ ] 每项简化都是可审核的增量修改
- [ ] diff 清晰，没有混入无关变更
- [ ] 遵循适用的 AGENTS.md、CLAUDE.md 和项目约定
- [ ] 没有删除或削弱错误处理
- [ ] 范围内候选已处理，或有具体保留理由；可达性检查包含初始化、注册、构建条件和公开调用方
- [ ] 团队成员或审核者会认可整体质量提升

按项目的验证范围使用隔离资源。纯命名、格式和等价直返无需新建测试套件。不削弱测试，也不为方便验证修改生产 API。报告实际检查、跳过项及环境缺口；独立复核遵循项目要求，不固定 Agent 数量。
