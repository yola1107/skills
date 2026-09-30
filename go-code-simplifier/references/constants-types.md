# Constants and Type Expressions

Use this reference when cleanup touches constants, enum-like declarations, numeric conversions, or declaration forms.

## Strict rule

A shorter constant expression is not automatically equivalent. Preserve concrete type, typed-versus-untyped constant semantics, conversion point, precision, overflow behavior, exported names, numeric values, and external representation.

## Redundant conversions

A conversion may be removed only when the surrounding declaration/expression still guarantees the same concrete type and conversion point.

Safe candidate:

```go
var ratio float64 = float64(0.1)
```

may become:

```go
var ratio float64 = 0.1
```

because the declared variable type still performs the same conversion.

Do not generalize this into “remove T(x)”. For example, changing a typed constant to an untyped constant, moving a float32/float64 conversion across arithmetic, or changing integer conversion/overflow timing can alter behavior.

## Typed and untyped constants

Treat typed ↔ untyped changes as behavior-sensitive. Untyped constants have different representability and default-type rules and can participate differently in later expressions.

Do not remove an explicit constant type merely for brevity unless all uses and resulting semantics are proven equivalent.

## Constant grouping

Separate declarations that form one clear domain may be grouped without changing names, types, values, order-sensitive semantics, or comments:

```go
const statusOK = 1
const statusBad = 2
```

may become:

```go
const (
	statusOK  = 1
	statusBad = 2
)
```

Grouping is organizational. It is not permission to renumber, alias, rename exported constants, or introduce `iota`.

## iota

Do not convert explicit numeric constants to `iota` merely because the current sequence matches. Explicit values may be protocol, persistence, database, RPC, wire, or compatibility contracts, and future insertion semantics differ.

Likewise, do not add an Unknown/Invalid zero sentinel or shift existing enum values during strict cleanup. That may be good new-code design guidance, but it changes existing behavior.

Existing `iota` declarations may be reformatted or privately renamed only when values remain identical.

## Same value does not mean same concept

Never merge constants merely because their values are equal. `UserActive = 1` and `OrderPaid = 1` are different domain concepts.

Alias/deduplication requires proof that the declarations represent the same domain concept and that names are not external/source compatibility contracts. Exported aliases are report-only by default.

## Naming

For private constants, use concise MixedCaps names that describe role rather than value and follow repository terminology. Avoid ALL_CAPS, value-derived names, and unexplained abbreviations when a safe local rename improves clarity.

Exported constant/enum renames are report-only by default.

Acronym and anti-stutter guidance is a candidate rule, not authority to break compatibility.

## Declaration style

Do not mechanically replace `var x T = value` with `x := value` or vice versa. Declaration form can affect scope, inferred type, zero-value intent, and package-level legality. Simplify only when those properties are unchanged.
