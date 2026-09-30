# Concurrency and Lifecycle

Preserve lock scope/order/protected invariant and whether external calls happen under lock. Preserve goroutine sync/async completion, cancellation, ownership, error propagation, waiting, panic handling and resource lifetime. Preserve channel capacity, blocking/backpressure, order, close ownership/timing, nil behavior and select semantics. Preserve context parent/values/cancellation/deadline scope. Preserve resource ownership/cleanup/rollback/pool timing and lifecycle init/start/register/ready/stop/drain/unregister/close order.

Race-clean verification is useful but does not prove deadlock, ordering or lifecycle equivalence.
