# 性能检查清单

本技能的性能审核参考。按需阅读前端、后端或 Go 章节，无需其他技能。下列阈值和命令需要结合项目负载、预算、数据库引擎及固定工具版本判断。审核保持只读，不为照搬示例而安装工具、修改索引、开启生产 profiling 或执行线上压测。

## 目录

- [Core Web Vitals 指标](#core-web-vitals-指标)
- [TTFB 排查](#ttfb-排查)
- [前端检查](#前端检查)
- [后端检查](#后端检查)
- [缓存策略](#缓存策略)
- [Go 服务](#go-服务)
- [测量命令](#测量命令)
- [常见反模式](#常见反模式)

## Core Web Vitals 指标

| 指标 | 良好 | 需要改善 | 较差 |
|--------|------|------------|------|
| LCP（最大内容绘制） | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| INP（交互到下一次绘制） | ≤ 200ms | ≤ 500ms | > 500ms |
| CLS（累计布局偏移） | ≤ 0.1 | ≤ 0.25 | > 0.25 |

## TTFB 排查

首字节时间较慢（>800ms）时，在 DevTools Network 瀑布图中分别检查：

- [ ] **DNS 解析**慢：为已知来源使用 `<link rel="dns-prefetch">` 或 `<link rel="preconnect">`
- [ ] **TCP/TLS 握手**慢：启用 HTTP/2，考虑边缘部署，核对连接复用
- [ ] **服务端处理**慢：分析后端 profile、慢查询和缓存需求

## 前端检查

### 图片
- [ ] 使用 WebP、AVIF 等现代图片格式
- [ ] 使用 `srcset` 和 `sizes` 提供适合屏幕尺寸的图片
- [ ] 图片和 `<source>` 明确设置 `width`、`height`，避免按布局切换图片时发生 CLS
- [ ] 首屏外图片设置 `loading="lazy"` 和 `decoding="async"`
- [ ] 首屏主图/LCP 图片设置 `fetchpriority="high"`，不使用懒加载

### JavaScript
- [ ] 首次加载的包体积在 gzip 压缩后低于 200KB
- [ ] 路由和重型功能通过动态 `import()` 拆包
- [ ] 开启 tree shaking，确认依赖提供 ESM 并声明 `sideEffects: false`
- [ ] `<head>` 中没有阻塞脚本，使用 `defer` 或 `async`
- [ ] 适用时把重计算移到 Web Workers
- [ ] 对相同 props 下仍重复渲染的高成本组件使用 `React.memo()`
- [ ] 仅在 profiling 显示收益时使用 `useMemo()` / `useCallback()`
- [ ] 拆分超过 50ms 的长任务，使主线程能及时响应，这是改善 INP 的重要手段
- [ ] 长循环使用 `yieldToMain` 一类模式，让输入事件能在分段之间执行
- [ ] 可用时采用现代调度 API：优先 `scheduler.yield()`，或带优先级的 `scheduler.postTask()`，以及用于按需让出的 `isInputPending()`
- [ ] 可推迟的非紧急工作使用 `requestIdleCallback`，例如分析数据刷新、预取、预热
- [ ] 分析、日志等非关键工作延后执行，避免阻塞事件处理和交互反馈
- [ ] 第三方脚本使用 `async` / `defer`，检查体积；聊天挂件和嵌入等重型组件先使用轻量占位界面

### CSS
- [ ] 关键 CSS 内联或预加载
- [ ] 非关键样式不阻塞渲染
- [ ] 生产环境避免 CSS-in-JS 运行时开销，采用构建时提取

### 字体
- [ ] 控制在 2–3 个字体族、每个 2–3 种字重；额外字重会增加请求
- [ ] 只提供 WOFF2，利用其最小体积和通用支持，省去 WOFF/TTF/EOT 版本
- [ ] 条件允许时自托管，避免第三方字体 CDN 带来的额外 DNS、TCP、TLS 往返
- [ ] LCP 关键字体预加载：`<link rel="preload" as="font" type="font/woff2" crossorigin>`
- [ ] 使用 `font-display: swap`，非关键字体可选 `optional`，避免不可见文本阻塞展示
- [ ] 使用 `unicode-range` 拆分字形，仅发送页面所需内容
- [ ] 需要多种字重/样式时考虑可变字体，用一个文件替代多个文件
- [ ] 使用 `size-adjust`、`ascent-override`、`descent-override` 调整回退字体度量，减少字体切换造成的 CLS
- [ ] 引入自定义字体前先考虑系统字体

### 网络
- [ ] 静态资源使用较长 `max-age` 和内容哈希
- [ ] 适合缓存的 API 响应配置 `Cache-Control`
- [ ] 启用 HTTP/2 或 HTTP/3
- [ ] 对已知来源使用 `<link rel="preconnect">`
- [ ] 关键的非图片资源也使用 `fetchpriority`，例如关键的 `<link rel="preload">` 和首屏 `<script>`，不限于 `<img>`
- [ ] 没有不必要的重定向

### 渲染
- [ ] 避免反复读写布局引发强制同步布局
- [ ] 动画使用 `transform` 和 `opacity`，利用 GPU 加速
- [ ] 长列表使用虚拟化，例如 `react-window`
- [ ] 避免不必要的整页重复渲染
- [ ] 屏幕外区域使用 `content-visibility: auto` 和 `contain-intrinsic-size`，跳过不可见内容的布局/绘制
- [ ] 避免 `unload` 监听和 HTML 响应上的 `Cache-Control: no-store`，保留使用前进/后退缓存 bfcache 的条件

## 后端检查

### 数据库
- [ ] 没有 N+1 查询，采用预加载或 join
- [ ] 查询具有合适索引
- [ ] 列表结果有界且排序明确；结合选择的列和数据量判断，不把所有 `SELECT *` 都认定为缺陷
- [ ] 已配置连接池
- [ ] 已启用慢查询日志

#### 执行计划
- [ ] 语法、节点名和索引能力符合实际数据库版本；下文的 `Seq Scan`、部分索引和 trigram 索引是 PostgreSQL 示例，不能直接当作 MySQL 指令
- [ ] 采集方式适合已确认的环境；基于执行的分析会实际运行查询，不能默认用于线上目标
- [ ] 在修复**之前**采集 `EXPLAIN ANALYZE`，建立可对照基线
- [ ] 已理解大表 `Seq Scan` 的原因：缺少索引、索引不可用，或使用索引确实不划算
- [ ] 估算与实际 `rows=` 相差不超过一个数量级；否则先更新统计信息再判断索引
- [ ] 不存在可以由组合索引承担的多余 `Sort`
- [ ] 获准优化时，对照前后的计划、实测成本和写入开销；计划形状未变本身不能判定索引无用

#### 索引策略
- [ ] 组合索引按等值条件优先、范围/排序随后安排
- [ ] 索引匹配完整查询形状，包括过滤和排序，而不只孤立关注某一列
- [ ] 热点读取考虑覆盖索引，减少回表
- [ ] 不为低选择性列的主要取值机械加索引；部分索引仍可能适合少见值，例如 `WHERE status = 'failed'`
- [ ] 查询对列应用函数时，检查表达式索引，例如 `lower(email)`
- [ ] 前导通配符查询使用全文或 trigram 等适合的索引，而不是普通 B-tree
- [ ] 对写入密集表测量写入成本，每个索引都会增加 `INSERT` / `UPDATE` 开销
- [ ] 疑似无用或重复索引需结合约束、调用方和代表性负载核对；审核只报告候选，不执行删除

#### 连接池
- [ ] 连接池有明确负责方，相同连接配置复用；不同数据库、凭据/角色或主从契约可以需要独立池
- [ ] 各实例相关连接池上限之和不超过对应数据库的连接预算
- [ ] 获取连接和查询等待符合有界的请求/Context 策略；使用实际驱动选项，`connectionTimeoutMillis` 是 Node 客户端示例
- [ ] 扩池前定位耗尽原因，确认是否由长事务、遗漏 `await`、客户端泄漏等长期占用连接
- [ ] Serverless 或自动扩容场景通过 pgbouncer、RDS Proxy 等复用代理控制连接，而不是只提高连接池上限

### API
- [ ] 响应时间分位数符合服务实测或约定预算；200ms p95 是示例，不是统一门槛
- [ ] 请求路径的计算满足延迟和资源契约；同步工作满足契约时可以保留
- [ ] 适合批量处理的操作避免逐项调用
- [ ] 响应使用 gzip/brotli 压缩
- [ ] 合理选择进程内、Redis、CDN 等缓存

### 基础设施
- [ ] 静态资源使用 CDN
- [ ] 服务靠近用户，或采用边缘部署
- [ ] 需要时配置水平扩容
- [ ] 为负载均衡提供健康检查接口

## 缓存策略

只有明确了成本和复用模式后才选择缓存层。先定义缓存键、负责方、内存上限、失效条件和可接受的数据过期窗口。缓存必须保持租户、授权和数据新鲜度契约。下列模式用于评估方案，不授权在审核中新增缓存。

### 读写模式

| 模式 | 工作方式 | 适用情况 | 注意事项 |
|---|---|---|---|
| **Cache-aside（旁路缓存、按需加载）** | 应用先查缓存，未命中时读取源数据并填充 | 常见选择，读多且允许首次冷缓存开销 | 每次未命中都会访问源，需要防止热点击穿 |
| **Read-through（穿透读取）** | 缓存层在未命中时负责加载 | 希望读取逻辑集中维护 | 源延迟被隐藏在缓存调用中，源慢会表现为缓存慢 |
| **Write-through（同步写入）** | 请求路径同步更新源和缓存 | 应用有明确一致性协议 | 两次写入不自动具备原子性，需定义顺序、部分失败、失效及并发读行为 |
| **Write-behind / Write-back（异步回写）** | 先写缓存，再异步更新源 | 写入较多且源是瓶颈 | 刷回之前缓存故障会丢数据，需要有依据的持久性保障 |

### 空结果缓存

也缓存“结果不存在”的情况。不断查询不存在的用户 ID 或 404 资源会让每次请求都访问源，单纯缓存成功结果无法覆盖这条路径。

- 存储明确的“不存在”标记，TTL 比正常结果**更短**
- 空结果 TTL 应足够短，使新建记录能及时被读取
- 不把源的**错误**当作不存在结果缓存，避免把短暂故障延长

### 合并并发请求

同一键由一次重算服务多个等待者，避免热点键过期后所有并发请求同时冲击源：

```typescript
const inFlight = new Map<string, Promise<unknown>>();

function loadOnce<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const existing = inFlight.get(key) as Promise<T> | undefined;
  if (existing) return existing;
  const p = fetcher().finally(() => inFlight.delete(key));
  inFlight.set(key, p);
  return p;
}
```

进程内合并不会跨实例去重。先判断是否确实需要跨实例协调；只有契约允许返回过期数据时才适合 stale-while-revalidate。不默认增加分布式锁。

### 缓存检查
- [ ] 已测得被缓存调用有明显成本；缓存本来很快的调用可能只增加跳转
- [ ] 读写比例支持缓存，即重复读取明显多于修改
- [ ] 缓存键包含影响响应的全部输入：租户、访问者、语言地区、权限、功能开关
- [ ] 用户专属数据不会缓存在缺少用户身份的键下
- [ ] 明确选择 TTL、事件/标签或版本化键等失效策略，避免无意混合
- [ ] 明确记录可接受的数据过期窗口，而非仅凭随手设置的 TTL
- [ ] 热点键具有请求合并、锁或 stale-while-revalidate 等防击穿机制
- [ ] 空结果使用更短 TTL，不缓存源错误
- [ ] 有淘汰策略和内存上限；判断泄漏前先确认实际增长与生命周期
- [ ] 监测命中率；没有测量的缓存只是未经验证的假设，低命中率意味着缓存只增加了开销
- [ ] 不缓存任何“过期即错误”的数据，例如结算时必须准确的余额、权限或库存

## Go 服务

- 区分等待连接或锁、执行查询和实际工作的耗时。按证据需要检查 database/sql 连接池统计、请求截止时间，以及已有 CPU/heap/block/mutex profile。
- 检查 goroutine 数量、队列和在途字节、被保留的 slice 底层数组及缓存上限。分配计时器或某时刻 goroutine 数量增长，本身不能证明泄漏。
- 根据不变量和实际负载选择 Mutex、RWMutex、atomic、sync.Map 或对象池，不凭“读多”标签或假设的速度选择。复用计时器必须保持起算和重置语义，周期 ticker 不自动等价于每次工作结束后的延迟。
- 获准优化时，使用已有的代表性 benchmark，并保持工具链、平台、输入、样本预算和缓存状态可比。区分改进与运行噪声，同时检查正确性。
- 通过项目入口运行受影响包的测试/vet 和必需的 race 检查。race、负载测量和大样本统计回答不同问题，不能互相替代，也不自动要求全做。

已有基准的命令示例，使用前替换包名和基准名，并确认资源隔离：

```sh
go test ./path/to/package -run '^$' -bench '^BenchmarkOperation$' -benchmem -count=5
go tool pprof ./cpu.prof
```

没有适用测量时，说明证据缺口，不编造延迟收益，也不改变生产 profiling 配置。

## 测量命令

使用已安装或仓库固定版本的工具。下列 Web 命令只展示能力，不授权通过 npx 下载未固定版本的工具或探测线上服务。Go 任务使用上一节和项目自身的入口。

### INP 真实用户数据与 DevTools 流程

1. **先看真实用户数据**：优化前通过 [CrUX Vis](https://developer.chrome.com/docs/crux/vis) 或项目 RUM 工具查看 INP。
2. **定位慢交互**：打开 DevTools → Performance，录制交互，查找点击或按键触发的长任务。
3. **在中档 Android 设备上验证**：INP 问题可能只在较慢硬件上出现，使用真机或 DevTools 的 4×–6× CPU 降速。

```bash
# Lighthouse 命令行
npx lighthouse https://localhost:3000 --output json --output-path ./report.json

# 分析包体积
npx webpack-bundle-analyzer stats.json
# Vite 项目也可使用：
npx vite-bundle-visualizer

# 检查包体积
npx bundlesize

# 在代码中采集 Web Vitals
import { onLCP, onINP, onCLS } from 'web-vitals';
onLCP(console.log);
onINP(console.log);
onCLS(console.log);

# 采集包含交互归因信息的 INP
import { onINP } from 'web-vitals/attribution';
onINP(({ value, attribution }) => {
  const { interactionTarget, inputDelay, processingDuration, presentationDelay } = attribution;
  console.log({ value, interactionTarget, inputDelay, processingDuration, presentationDelay });
});
```

## 常见反模式

| 反模式 | 影响 | 处理方向 |
|---|---|---|
| N+1 查询 | 数据库负载随条目数线性增长 | 使用 join、预加载或批量读取 |
| 无界查询 | 内存耗尽、超时 | 分页并设置 LIMIT |
| 缺少索引 | 数据增长后读取变慢 | 为过滤和排序列设计适当索引 |
| 未看计划就加索引 | 增加写入成本，读取收益未确认 | 在授权环境下对照适当执行计划和测量 |
| 重复或无用索引 | 每次写入都承担额外成本 | 检查使用情况、约束和调用方，再建议删除 |
| 每请求创建连接池 | 负载上升时可能耗尽连接预算 | 按连接配置/角色复用连接池，并统筹各实例预算 |
| 缓存键缺少访问者 | 一个用户的数据可能返回给另一个用户 | 包含租户、访问者、地区和权限 |
| 无界缓存 | 保留数据可以无限增长 | 设置淘汰策略和内存上限 |
| 热点键缓存击穿 | 过期时全部并发请求冲击源 | 合并未命中请求，或使用 stale-while-revalidate |
| 反复触发布局 | 卡顿、掉帧 | 批量读取 DOM，再批量写入 |
| 图片未优化 | LCP 慢、浪费带宽 | 使用 WebP、响应式尺寸和懒加载 |
| 包体积过大 | 可交互时间变长 | 拆包、tree shaking、审核依赖 |
| 主线程被阻塞 | INP 差、UI 无响应 | 使用 `scheduler.yield()` / `yieldToMain` 分段，或交给 Web Workers |
| 内存泄漏 | 内存持续增长并最终崩溃 | 清理监听器、计时器和引用 |
