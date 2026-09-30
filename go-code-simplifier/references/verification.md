# Verification

Verification supports equivalence; it does not replace reasoning about behavior.

## Baseline
Before production edits, establish the cleanup baseline and record relevant existing failures. In a dirty worktree, baseline is the actual starting state, not `HEAD`.

## Characterization evidence
If existing evidence is insufficient for a behavior-sensitive candidate, prefer skipping the candidate.

Add characterization tests only when:
- the cleanup has meaningful value;
- test edits are inside authorized mutation scope;
- the test records existing observable behavior rather than redefining it.

For effectful flows, useful evidence includes call parameters/count/order, failure points, state changes, cleanup, and partial results.

## Batch verification
After each small coherent batch, run the narrowest useful checks. Expand with blast radius: affected package → dependents/modules → broader suite/build. Add race checks for concurrency-sensitive paths.

Prefer repository-native Make/Task/scripts/CI commands and configured format/lint tooling. Do not invent a competing workflow.

Typical Go commands, adjusted to repository layout, may include:
```bash
go test -count=1 <affected-packages>
go vet <affected-packages>
go build <affected-packages-or-module>
go test -race -count=1 <affected-packages>
git diff --check
```

## Failure policy
If cleanup causes failure, fix or revert that cleanup. Never weaken assertions, expected behavior, types, lint rules, exclusions, or test selection merely to make cleanup pass.

## Final evidence
Final claims require fresh checks on the final relevant state. A later edit invalidates checks it can affect. Report exact commands/outcomes, pre-existing failures, and checks not run.
