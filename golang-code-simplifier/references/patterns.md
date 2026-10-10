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

**嵌套超限：先跳出，再提取职责独立的分支** [B] 前提：提取后锁的配对、调用顺序和日志不变（见 traps.md「控制流」「并发」）。

```go
// 改前：for → for → if → if/else → for → if，下注和换区两个分支各二三十行
func (r *Room) RunAI(task *timewheel.Task, args ...interface{}) {
	...
	for _, ai := range r.ais {
		for _, action := range ai.Action {
			if action.Time == r.aiindex {
				if action.Action == 1 {
					// 三十行：查找或创建下注信息、加锁写入、统计、追加 playerbet 消息
				} else {
					// 二十多行：读锁内改区域并统计、if ok 追加消息 else 记日志
				}
			}
		}
	}
	...
}

// 改后：循环体只剩分派，每个分支一个方法
func (r *Room) RunAI(task *timewheel.Task, args ...interface{}) {
	...
	for _, ai := range r.ais {
		for _, action := range ai.Action {
			if action.Time != r.aiindex {
				continue
			}
			if action.Action == 1 {
				msgs = append(msgs, r.aiBet(ai, action))
				continue
			}
			if msg, ok := r.aiSwitchPot(ai, action); ok {
				msgs = append(msgs, msg)
			}
		}
	}
	...
}

// aiSwitchPot 把 AI 的下注移到 action 指定的区域，AI 没有下注记录时返回 false。
func (r *Room) aiSwitchPot(ai *pb.BR001AI, action *pb.BR001AIAction) (*pb.UserMessage, bool) {
	r.betlock.RLock()
	bet, ok := r.playersbet[ai.Uid]
	var oldPID int32
	if ok {
		oldPID = bet.Pid
		bet.Pid = action.Pid
	}
	r.betlock.RUnlock()
	if !ok {
		r.module.Errorln("AI NO KEYYP!")
		return nil, false
	}
	return modules.ToUserMessage("br001/playerswitchpot", &pb.BR001PlayerSwitchPotPush{
		Uid:        bet.Uid,
		Playername: bet.Playername,
		Oldpid:     oldPID,
		Newid:      action.Pid,
		Allbet:     bet.Bet,
	}), true
}
```

逐项核对：
- 提取出的方法里，`RLock` 与 `RUnlock` 之间没有新增的返回点，`return` 都在解锁之后。
- 消息追加的顺序、`Errorln` 的触发条件和文本与原来相同。
- 原代码在读锁内累加的 `oldPotTotalBet`、`newPotTotalBet` 只被自己读取，`utils.Add` 无副作用，属于死计算，可以一并删除（B 级）；删除前确认函数内没有其他读取。
- 在 `RLock` 下修改 `bet.Pid` 是原有的数据竞争，写进「发现」，不在简化中修复。

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

## 命名

**按内容和职责命名** [A] 局部变量、未导出函数内的名字；前提见 traps.md「命名」。

```go
// 改前：_session 和 session 只差一个下划线，读者分不清哪个是房间里保存的会话；
// ok1、ok2 要回头看赋值才知道各自代表什么。
_session, ok1 := r.sessions[session.GetUserId()]
userinfo, ok2 := r.playersbet[session.GetUserId()]
if !ok1 || !ok2 || userinfo.Pid == -1 {
	return errNoPot
}

// 改后
uid := session.GetUserId()
roomSession, hasSession := r.sessions[uid]
betInfo, hasBet := r.playersbet[uid]
if !hasSession || !hasBet || betInfo.Pid == -1 {
	return errNoPot
}
```

`uid := session.GetUserId()` 把两次调用合并成一次，需要先确认 `GetUserId` 没有副作用、两次调用之间返回值不变（B 级）。

**长短与作用域相称**

```go
// 短作用域：短名就够
for i, p := range r.pools {
	total = utils.Add(total, p.GetBetmoney(), r.aibets[i])
}

// 跨越几十行的变量：完整名字，带单位
startMilli := time.Now().UnixMilli()   // 原名 ts
settleSec := r.starttime / 1000        // 原表达式直接写在调用参数里，单位不明
```

**结果与返回值** [A]

```go
// 改前
func (m *model) getlog(buildid string, page, size int) (ret []*pb.Log, e error)

// 改后：结果名说明内容，错误统一叫 err，缩写写成 ID
func (m *model) getlog(buildID string, page, size int) (logs []*pb.Log, err error)
```

**参数遮蔽内置名** [B]

```go
// 改前：参数 min 遮蔽了内置 min，函数体里想用内置函数时会编译失败或误用
func SplitInt(total, min float64, num int32) []float64

// 改后：导出函数的参数名不属于函数类型，调用方不受影响
func SplitInt(total, minUnit float64, num int32) []float64
```

**保持原样的名字**：receiver `this` 是本仓库的统一写法；`pb` 生成的字段名（`Agentid`、`Pid`）和导出方法名（`SendMsgForMapSessios`）改名会影响协议或调用方，拼写问题列入「发现」。

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

## 反例

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
