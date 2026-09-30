# Safety Gate

A missed cleanup opportunity is acceptable. An unproven behavior change is not.

Decision priority: **safety / behavior equivalence > clarity > simplicity > brevity**. If a shorter form hides a boundary check, error path, ownership rule, side effect, or important domain step, keep the explicit form.

Apply only when the simplification benefit is concrete, relevant observable behavior is understood, equivalence is explainable, mutation stays in scope, and verification can detect likely regressions.

Observable behavior includes inputs/defaults/validation, outputs/nil state, errors, state mutation, external calls, call count/order, resource lifetime, synchronization/blocking, cancellation/lifecycle, serialization/protocol/config/persistence, registration/reflection, time/random consumption and public compatibility.

## Never auto-apply style fixes
Do not automatically normalize nil collections; add/remove defensive copies or error wrapping/logging; redesign signatures; change receivers; move cleanup into/out of defer; reorder guards/effects; replace independent branches with exclusive ones; add caching/preallocation/batching/parallelism; alter goroutine/channel/context/lock/lifecycle behavior; rename/unexport public identifiers; or change API/protocol/config/schema/persistence representation.

“No direct references” is not proof of dead code. Check interfaces, reflection, registries, init, blank imports, generated code, build tags/platform files, string/config names and external callers.

If uncertain or verification fails, revert only that cleanup; never overwrite pre-existing user edits.


## No cleverness tax

A cleanup must not replace straightforward Go with a more dynamic or expensive mechanism merely to reduce repetition or line count.

Do not introduce solely for simplification:
- reflection or runtime type inspection;
- `unsafe`;
- complex generic/type-constraint machinery;
- closure factories, callback layers, or higher-order indirection that obscures control flow;
- new interface/dynamic-dispatch layers without an existing abstraction need;
- allocation-heavy helper structures or conversions.

Existing uses of these mechanisms may be simplified locally when behavior is preserved; this rule prevents introducing them as the simplification technique.

Prefer explicit branches, concrete types, direct calls, and ordinary loops when they are clearer. A slightly longer direct implementation is preferable to a shorter abstraction with higher runtime or cognitive cost.
