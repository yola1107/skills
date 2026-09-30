# Verification

Establish a baseline before production edits. In a dirty worktree, baseline is the actual starting state, not HEAD.

When tests do not pin behavior a candidate may affect, add focused characterization tests against the old implementation first. For effectful flows capture call parameters/count/order, failure points, state changes, cleanup and partial results.

After each small coherent batch run the narrowest useful checks. Expand with blast radius: affected package → dependents/modules → broader suite/build; add race checks for concurrency-sensitive paths. Prefer repository-native Make/Task/scripts/CI commands.

Typical commands, adjusted to repository layout: go test -count=1, go vet, go build, go test -race -count=1, git diff --check.

If cleanup causes failure, fix or revert that cleanup. Never weaken assertions, expected behavior, types or test selection to make it green.

Final claims require fresh checks on final relevant state. Report exact commands/outcomes, pre-existing failures, and checks not run.
