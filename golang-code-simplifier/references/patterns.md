# 改写示例

示例取自真实代码。receiver 用短名只为排版，实际沿用项目写法（如 `this`）。

## 控制流

**循环体用 continue 展平**

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

**嵌套超限：先跳出，再提取独立的分支**（前提见 traps.md「控制流」「并发」）

```go
// 改前：for → for → if → if/else → for → if，两个分支各二三十行
for _, ai := range r.ais {
	for _, action := range ai.Action {
		if action.Time == r.aiindex {
			if action.Action == 1 {
				// 三十行：查找或创建下注信息、加锁写入、追加 playerbet 消息
			} else {
				// 二十多行：读锁内改区域、if ok 追加消息 else 记日志
			}
		}
	}
}

// 改后：循环体只剩分派
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

核对要点：
- `RLock` 与 `RUnlock` 之间没有新增返回点。
- 消息顺序、`Errorln` 的触发条件和文本不变。
- 原代码在读锁内累加的 `oldpoolsallbet`、`newpoolsallbet` 只供已注释掉的日志使用，`utils.Add` 无副作用，可以连同注释一起删除。
- 持有 `RLock` 时修改 `bet.Pid` 是数据竞争，写进「发现」。

## 作用域

**声明移到使用处，删除重复初始化**

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

`len(players) == 0` 时两种写法都得到空切片而不是 nil。

## 命名

```go
// 改前：_session 与 session 只差一个下划线；ok1、ok2 要回头看赋值才知道含义
_session, ok1 := r.sessions[session.GetUserId()]
userinfo, ok2 := r.playersbet[session.GetUserId()]
if !ok1 || !ok2 || userinfo.Pid == -1 {
	return errNoPot
}

// 改后（合并两次调用前，确认 GetUserId 无副作用）
uid := session.GetUserId()
roomSession, hasSession := r.sessions[uid]
betInfo, hasBet := r.playersbet[uid]
if !hasSession || !hasBet || betInfo.Pid == -1 {
	return errNoPot
}
```

```go
// 结果名说明内容，错误统一叫 err，缩写写成 ID
func (m *model) getlog(buildid string, page, size int) (ret []*pb.Log, e error)
func (m *model) getlog(buildID string, page, size int) (logs []*pb.Log, err error)

// 参数遮蔽内置 min；参数名不属于签名，调用方不受影响
func SplitInt(total, min float64, num int32) []float64
func SplitInt(total, minUnit float64, num int32) []float64
```

保持原样：receiver `this`、`pb` 生成的字段名（`Agentid`、`Pid`）、导出方法名（`SendMsgForMapSessios`），拼写问题列入「发现」。

## 错误处理与返回值

**多返回点的裸 return 改为显式返回**

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

**带日志的错误分支保留显式 return**

```go
// 改前
if err = db.GameDB().CreateTable(TableBr001log, &pb.DBBR001Log{}); err != nil {
	this.module.Errorln(err)
	return
}
return

// 不要改成：调用移出了 if，错误分支没有 return，
// 以后在 return err 之前追加的代码会在出错时执行
err := db.GameDB().CreateTable(TableBr001log, &pb.DBBR001Log{})
if err != nil {
	this.module.Errorln(err)
}
return err

// 去掉命名结果时这样改
if err := db.GameDB().CreateTable(TableBr001log, &pb.DBBR001Log{}); err != nil {
	this.module.Errorln(err)
	return err
}
return nil
```

## 锁内代码

**拉平锁外的嵌套，锁内结构不动，锁泄漏只报告**

```go
// 改前
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

// 改后：外层 if 改为提前返回；循环里的 return 原样保留
if len(models) == 0 {
	return
}
settings = make([]*pb.Setting, 0)
c.lock.Lock()
for _, m := range models {
	// ... 与原来相同 ...
}
c.lock.Unlock()
return
```

```markdown
- [严重][原有] `setting.go:14` `reload`：JSON 解析失败时持有 `c.lock` 返回，锁永不释放，后续读取全部阻塞。修复方向：先在锁外解析全部模型，再加锁一次性写入缓存。
```

## import 分组

`go.mod` 为 `module go_manwugame`，工具链 Go 1.21+：

```go
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

`go_manwugame` 不含点，按「第一段不含 `.`」会被误判为标准库，所以先按 module 前缀识别本项目。

## 反例

```go
// 合并失败处理不同的代码：一个忽略 ErrNotFound、一个返回它，不能抽成同一个 helper
if err := loadBag(id); err != nil && !errors.Is(err, ErrNotFound) {
	return err
}
if err := loadMail(id); err != nil {
	return err
}

// 为了短改成立即执行的闭包，比原来的 if 更难读
level := func() int { if exp >= nextLevelExp { return 2 }; return 1 }()

// 条件取反后没同步注释
if atomic.LoadInt32(&r.state) != 1 { // 下注中   ← 应改为「不在下注阶段」
	return errNotBetting
}
```
