# Safety Gate

A missed cleanup opportunity is acceptable. An unproven behavior change is not.

Apply only when the simplification benefit is concrete, relevant observable behavior is understood, equivalence is explainable, mutation stays in scope, and verification can detect likely regressions.

Observable behavior includes inputs/defaults/validation, outputs/nil state, errors, state mutation, external calls, call count/order, resource lifetime, synchronization/blocking, cancellation/lifecycle, serialization/protocol/config/persistence, registration/reflection, time/random consumption and public compatibility.

## Never auto-apply style fixes
Do not automatically normalize nil collections; add/remove defensive copies or error wrapping/logging; redesign signatures; change receivers; move cleanup into/out of defer; reorder guards/effects; replace independent branches with exclusive ones; add caching/preallocation/batching/parallelism; alter goroutine/channel/context/lock/lifecycle behavior; rename/unexport public identifiers; or change API/protocol/config/schema/persistence representation.

“No direct references” is not proof of dead code. Check interfaces, reflection, registries, init, blank imports, generated code, build tags/platform files, string/config names and external callers.

If uncertain or verification fails, revert only that cleanup; never overwrite pre-existing user edits.
