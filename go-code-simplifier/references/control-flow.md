# Control Flow

Prefer explicit flow over clever compactness. Keep the normal path at minimal indentation when an equivalent early error/edge-case exit makes it easier to scan.

Candidates: remove unnecessary else after return/break/continue; guard clauses that preserve exact failure/effect order; reduce nesting without moving effects; consolidate genuinely identical branches; name complex conditions when meaning improves without defeating short-circuit behavior.

Preserve independent versus exclusive branch behavior, condition/function evaluation order, short-circuiting, call count, error precedence, mutation/effect timing, loop-control target and panic/recover boundaries.

Do not mechanically convert independent ifs to else-if/switch, repeated reads to cached reads, multiple returns to one exit, or effectful expressions to eagerly evaluated helper arguments.
