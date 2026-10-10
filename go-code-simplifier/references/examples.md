# 改写示例

示例取自真实代码。receiver 用短名只为排版，实际沿用项目写法（如 `this`）。

## 嵌套超限：先跳出，再提取独立的分支

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
- 原代码在读锁内累加的两个合计值只供注释掉的日志使用，`utils.Add` 无副作用，连同注释一起删除。
- 持有 `RLock` 时修改 `bet.Pid` 是竞态，写进「发现」。

## 带日志的错误分支保留显式 return

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

## 拉平锁外的嵌套，锁泄漏只报告

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

// 改后：外层 if 改为提前返回；锁内的循环和 return 原样保留
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
- [严重] `setting.go:14` `reload`：JSON 解析失败时持有 `c.lock` 返回，锁永不释放，后续读取全部阻塞。修复方向：先在锁外解析全部模型，再加锁一次性写入缓存。
```

## 命名与重复初始化

```go
// 改前：_session 与 session 只差一个下划线；ok1、ok2 要回头看赋值才知道含义
_session, ok1 := r.sessions[session.GetUserId()]
userinfo, ok2 := r.playersbet[session.GetUserId()]

// 改后（合并两次调用前，确认 GetUserId 无副作用）
uid := session.GetUserId()
roomSession, hasSession := r.sessions[uid]
betInfo, hasBet := r.playersbet[uid]
```

```go
// 改前：函数开头初始化，几十行之后使用前又初始化一次
resultPlayers := make([]*pb.ResultItem, 0)
// ... 无关的几十行 ...
if len(players) > 0 {
	resultPlayers = make([]*pb.ResultItem, 0)
	// ... 填充 resultPlayers ...
}

// 改后：只初始化一次，紧挨使用位置；players 为空时仍是空切片而不是 nil
// ... 无关的几十行 ...
resultPlayers := make([]*pb.ResultItem, 0)
if len(players) > 0 {
	// ... 填充 resultPlayers ...
}
```
