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

**为一个调用点引入抽象**：只有一个实现、也没有测试替身的 interface，只被调用一次的泛型函数，都会让读者多跳一层，保持原样。
