# Uber Go Guidance

Use Uber Go Style Guide as a candidate source, never as authority over existing behavior.

Useful heuristics: readable explicit code, reduced nesting, deliberate interfaces/receivers, mutex encapsulation, ownership awareness for slices/maps, defer readability, deliberate errors, goroutine lifecycle, avoiding init magic, nil-slice awareness and consistent linting.

Never auto-apply ownership copies, nil/empty normalization, receiver changes, lock/defer changes, error wrapping/logging, goroutine lifecycle changes, init rewrites, or performance/preallocation advice in strict cleanup. First prove equivalence and repository fit.
