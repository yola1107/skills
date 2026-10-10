# 改写示例

每个示例标注等级和成立前提。前提不满足时按 SKILL.md「分级」降级处理。

## 控制流

**错误先返回** [A]

```go
// 改前
func load(id int64) (*Order, error) {
	o, err := repo.Get(id)
	if err == nil {
		if o.Status == StatusPaid {
			return o, nil
		} else {
			return nil, ErrNotPaid
		}
	} else {
		return nil, err
	}
}

// 改后
func load(id int64) (*Order, error) {
	o, err := repo.Get(id)
	if err != nil {
		return nil, err
	}
	if o.Status != StatusPaid {
		return nil, ErrNotPaid
	}
	return o, nil
}
```

**循环体用 continue 展平** [A]

```go
// 改前
for _, p := range players {
	if p.Online {
		if p.Level >= minLevel {
			send(p)
		}
	}
}

// 改后
for _, p := range players {
	if !p.Online || p.Level < minLevel {
		continue
	}
	send(p)
}
```

**同一变量的多分支改 switch** [B] 前提：分支内没有 `break`，比较对象不是函数调用（见 traps.md「控制流」）。

```go
// 改前
if kind == KindGold {
	addGold(n)
} else if kind == KindDiamond {
	addDiamond(n)
} else if kind == KindItem {
	addItem(id, n)
} else {
	return ErrUnknownKind
}

// 改后
switch kind {
case KindGold:
	addGold(n)
case KindDiamond:
	addDiamond(n)
case KindItem:
	addItem(id, n)
default:
	return ErrUnknownKind
}
```

## 冗余

**多余的 nil 判断与存在判断** [A] `len` 对 nil 切片、nil map 返回 0；`delete` 对不存在的键是空操作。

```go
// 改前
if items != nil && len(items) > 0 { ... }
if _, ok := cache[key]; ok {
	delete(cache, key)
}

// 改后
if len(items) > 0 { ... }
delete(cache, key)
```

**只转发一次的中间变量** [A]

```go
// 改前
result := buildReply(req)
return result, nil

// 改后
return buildReply(req), nil
```

保留能给计算步骤命名、或方便调试时打断点的中间变量。

## 作用域

**值只在 if 内使用时放进初始化语句** [A] 前提：中间没有其他语句读写同一状态。

```go
// 改前
n, err := w.Write(buf)
if err != nil {
	return fmt.Errorf("write: %w", err)
}
_ = n

// 改后
if _, err := w.Write(buf); err != nil {
	return fmt.Errorf("write: %w", err)
}
```

`if` 之后还要用到的值（例如 `cfg, ok := configs[id]` 之后的 `cfg`）保持在外层声明。

**声明移到使用的块内，删除重复初始化** [B] 前提：两次初始化之间没有读取（见 traps.md「作用域」）。

```go
// 改前：函数开头初始化，几十行之后使用前又初始化一次
resultPlayers := make([]*pb.ResultItem, 0)
// ... 与 resultPlayers 无关的几十行 ...
if len(players) > 0 {
	resp, errdata := m.settle(players)
	resultPlayers = make([]*pb.ResultItem, 0)
	if errdata == nil {
		for _, v := range resp.Data {
			resultPlayers = append(resultPlayers, toItem(v))
		}
	}
}
r.playerresult = resultPlayers

// 改后：只初始化一次，紧挨使用位置
// ... 与 resultPlayers 无关的几十行 ...
resultPlayers := make([]*pb.ResultItem, 0)
if len(players) > 0 {
	resp, errdata := m.settle(players)
	if errdata == nil {
		for _, v := range resp.Data {
			resultPlayers = append(resultPlayers, toItem(v))
		}
	}
}
r.playerresult = resultPlayers
```

`len(players) == 0` 时两种写法都得到空切片而不是 nil，值的形态不变。只把函数开头的 `var (...)` 块拆成一行行 `:=`、位置不动，不算收紧作用域。

## 错误处理

**合并末尾返回** [B] 前提：`err` 的静态类型是 `error`（见 traps.md「错误」）。

```go
// 改前
err := s.save(ctx, u)
if err != nil {
	return err
}
return nil

// 改后
return s.save(ctx, u)
```

## 返回值

**多返回点的裸 return 改为显式返回** [B] 前提：没有 `defer`/`recover` 读写结果（见 traps.md「返回值」）。

```go
// 改前：读者要回头查 errdata 在每个 return 处的值
func (r *rooms) bet(s Session, rid string, money float64) (errdata *pb.ErrorData) {
	room, ok := r.find(s, rid)
	if !ok {
		errdata = &pb.ErrorData{Code: pb.ErrorCode_NoFindRoom}
		return
	}
	errdata = room.Bet(s, money)
	return
}

// 改后
func (r *rooms) bet(s Session, rid string, money float64) *pb.ErrorData {
	room, ok := r.find(s, rid)
	if !ok {
		return &pb.ErrorData{Code: pb.ErrorCode_NoFindRoom}
	}
	return room.Bet(s, money)
}
```

**同类型多结果保留名字** [A]

```go
// 保留结果名说明含义，只把裸 return 改成显式
func bounds(xs []int) (lo, hi int) {
	...
	return lo, hi
}
```

## 收尾格式

**删除代码块首尾空行** [A]

```go
// 改前
if len(players) > 0 {

	resp, errdata := m.settle(players)
	...

}

// 改后
if len(players) > 0 {
	resp, errdata := m.settle(players)
	...
}
```

**import 按标准库、本项目、第三方分组** [A] `go.mod` 为 `module go_manwugame`，工具链 Go 1.21+。

```go
// 改前
import (
	"fmt"
	"go_manwugame/comm"
	"go_manwugame/pb"
	"github.com/mitchellh/mapstructure"
	"sync"
	log "go_manwugame/lego/sys/log"
	_ "github.com/go-sql-driver/mysql"
)

// 改后
import (
	"fmt"
	"sync"

	"go_manwugame/comm"
	log "go_manwugame/lego/sys/log"
	"go_manwugame/pb"

	_ "github.com/go-sql-driver/mysql"
	"github.com/mitchellh/mapstructure"
)
```

`go_manwugame` 不含点，按「第一段不含 `.`」会被误判为标准库，所以先按 module 前缀识别本项目包。组内顺序由 gofmt 按路径排序，别名和 `_` 导入保留原写法。

## 锁内代码

**展平锁外层的嵌套，锁内结构不动** [B] 前提：`Lock` 与 `Unlock` 的配对、覆盖的语句和执行顺序不变（见 traps.md「并发」）。

```go
// 改前
func (c *settingComp) reload(agentID string) (settings []*pb.Setting, err error) {
	models := make([]*pb.DBSetting, 0)
	if err = db.Find(&models, agentID); err != nil {
		return
	}
	if len(models) > 0 {
		settings = make([]*pb.Setting, 0)
		c.lock.Lock()
		for _, m := range models {
			s := &pb.Setting{}
			if err = json.Unmarshal(m.Data, s); err != nil {
				return
			}
			settings = append(settings, s)
			c.cache[m.Key] = s
		}
		c.lock.Unlock()
	}
	return
}

// 改后：外层 if 改为提前返回，没有模型时 settings 仍为 nil
func (c *settingComp) reload(agentID string) (settings []*pb.Setting, err error) {
	models := make([]*pb.DBSetting, 0)
	if err = db.Find(&models, agentID); err != nil {
		return
	}
	if len(models) == 0 {
		return
	}
	settings = make([]*pb.Setting, 0)
	c.lock.Lock()
	for _, m := range models {
		s := &pb.Setting{}
		if err = json.Unmarshal(m.Data, s); err != nil {
			return
		}
		settings = append(settings, s)
		c.cache[m.Key] = s
	}
	c.lock.Unlock()
	return
}
```

循环里的 `return` 在持有写锁时返回，锁不会释放，此后所有读锁都会阻塞；已写入缓存的部分配置也不会回滚。这是缺陷，不在简化中修复，报告为：

```markdown
- [严重] `setting.go:14` `reload`：JSON 解析失败时持有 `c.lock` 返回，锁永不释放，后续读取全部阻塞。修复方向：先在锁外解析全部模型，再加锁一次性写入缓存。
```

## 重复

**输入、副作用、顺序都相同的块提取为函数** [B] 前提：两处的输入来源、日志、写入的状态完全一致，提取后调用位置和顺序不变。

```go
// 改前：switch 的两个分支里各有一份
for i, p := range r.pools {
	total := utils.Add(p.GetBetmoney(), float64(r.aibets[i]))
	share := utils.Compute(total, 1-0.05)
	if utils.Sub(betall, total) != 0 {
		ratios[i] = utils.Div(share, utils.Sub(betall, total))
	}
}

// 改后：两个分支都调用
func (r *Room) carveupRatios(betall float64, ratios []float64) {
	for i, p := range r.pools {
		total := utils.Add(p.GetBetmoney(), float64(r.aibets[i]))
		share := utils.Compute(total, 1-0.05)
		if utils.Sub(betall, total) != 0 {
			ratios[i] = utils.Div(share, utils.Sub(betall, total))
		}
	}
}
```

一处带日志、另一处不带，或者两处读取的状态在调用之间会变化时，不算相同的块，保持原样或列为 C 级建议。

## 标准库写法

**`strings.Cut`**（1.18+）[B] 前提：原代码对缺少分隔符的情况已有处理（见 traps.md「标准库替换」）。

```go
// 改前
i := strings.Index(s, "=")
if i < 0 {
	return s, "", false
}
return s[:i], s[i+1:], true

// 改后
return strings.Cut(s, "=")
```

`strings.Cut` 未找到分隔符时返回 `s, "", false`。原代码未找到时返回 `"", "", false` 就不等价，保持原样。

**`slices.Contains`**（1.21+）[A]

```go
// 改前
found := false
for _, id := range ids {
	if id == target {
		found = true
		break
	}
}

// 改后
found := slices.Contains(ids, target)
```

**整数 range**（1.22+）[B] 前提：循环中不修改 `n` 和 `i`，`i` 的类型不变。

```go
// 改前
for i := 0; i < n; i++ { ... }

// 改后
for i := range n { ... }
```

## 反例：不要这样简化

**合并失败处理不同的两段代码**

```go
// 两段看起来一样，但一个忽略 ErrNotFound、一个返回它，不能抽成同一个 helper。
if err := loadBag(id); err != nil && !errors.Is(err, ErrNotFound) {
	return err
}
if err := loadMail(id); err != nil {
	return err
}
```

**为了短而牺牲可读性**

```go
// 改前：清楚
level := 1
if exp >= nextLevelExp {
	level = 2
}

// 不要改成立即执行的闭包
level := func() int { if exp >= nextLevelExp { return 2 }; return 1 }()
```

**删除错误分支末尾的 return**

```go
// 改前：保持原样
if err = db.Insert(logs); err != nil {
	m.Errorln(err)
	return
}
return

// 不要改成：以后在末尾追加的代码会在出错时执行
if err = db.Insert(logs); err != nil {
	m.Errorln(err)
}
return
```

**条件取反后留下过时注释**

```go
// 改前
if atomic.LoadInt32(&r.state) == 1 { // 下注中
	...
}

// 不要改成：注释说的是相反的情况
if atomic.LoadInt32(&r.state) != 1 { // 下注中
	return errNotBetting
}

// 改后
if atomic.LoadInt32(&r.state) != 1 { // 不在下注阶段
	return errNotBetting
}
```

**为一个调用点引入抽象**：只有一个实现、也没有测试替身的 interface，只被调用一次的泛型函数，都会让读者多跳一层，保持原样。
