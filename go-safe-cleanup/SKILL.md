---
name: go-safe-cleanup
description: Safety-first cleanup of existing Go code. Reduce redundancy, naming noise, local data-flow complexity, nesting, and shallow abstractions only when observable behavior can be shown to remain equivalent. Do not use to smuggle in bug fixes, optimizations, API changes, or concurrency/lifecycle redesign.
---

# Go Safe Cleanup

Clean Go code with one non-negotiable rule: **behavior equivalence comes first. If equivalence cannot be established, do not change the code.**

Optimize for lower cognitive load, clearer local flow, less redundancy, and fewer unnecessary concepts. Fewer lines, functions, or complexity points are not goals by themselves.

## Precedence
1. User scope and explicit constraints.
2. Repository-local rules and established contracts.
3. Behavior-equivalence and safety rules in this skill.
4. Go semantics for the repository's declared version.
5. Uber/Samber/style guidance only as candidate generators.

Always read `references/safety-gate.md` and `references/verification.md`. Load the matching pass reference and behavior-sensitive references only when relevant.

## Hard boundary
Do not mix cleanup with bug fixes, new validation, retries, caching, batching, performance redesign, API/protocol/config/schema changes, dependency upgrades, or concurrency/lifecycle redesign. Report them separately unless scope is explicitly expanded.

Treat pre-existing worktree changes as protected. Baseline is the actual state at cleanup start, not necessarily HEAD. Reading may extend beyond mutation scope to prove behavior; editing may not silently extend beyond it.

## Passes
**Pass 0 — Baseline:** resolve mutation scope, repository guidance, worktree/staged changes, Go module/workspace boundaries, and baseline checks. Record pre-existing failures. No production edits.

**Pass 1 — Behavior map:** read enough callers/callees/interfaces/tests/registrations/ownership/contracts to identify observable behavior. Build candidates. Add characterization tests first when important behavior is not pinned. No production logic edits.

**Pass 2 — Formatting/mechanical noise:** formatting, meaningless whitespace, proven redundant locals/wrappers, obvious expression noise, and comments that only restate code. Preserve semantic blank-line grouping, directives, rationale and invariants. Verify.

**Pass 3 — Naming/local data flow:** improve local/private names, remove meaningless intermediates, reduce scope, eliminate type-stuttering, and name state transitions. Name length follows scope/ambiguity. Preserve conventional short names such as ctx, err, ok, i, n, r, w. Exported renames are report-only by default. Verify.

**Pass 4 — Control flow:** reduce unnecessary nesting/else and clarify guards/branches only when evaluation order, call count, error precedence, mutations and side effects remain identical. Verify.

**Pass 5 — Local structure/redundancy:** remove only proven shallow private wrappers/helpers and semantic duplication. Keep business naming, synchronization, ownership, validation, instrumentation, compatibility and useful seams. Avoid generic abstractions or flag-driven mega-functions. Verify.

**Pass 6 — Strict equivalence audit:** stop improving. Assume prior cleanup may be wrong. Audit the full cleanup diff for errors, nil, aliasing, evaluation, defer, synchronization, context, lifecycle, external contracts, reflection/registration, time/randomness and side effects. Prove equivalence or revert the individual cleanup.

**Pass 7 — Final verification:** run repository-native checks on final state, expanding with blast radius. Typical checks: gofmt, go test -count=1, go vet, build, and -race when relevant. Inspect complete diff and git diff --check. Never claim a check passed unless run after the final relevant edit.

## Reviewers
If subagents exist, use them as reviewers, not concurrent editors: simplification reviewer, Go-equivalence reviewer, verification reviewer. Main agent decides. Efficiency findings are separate optimization candidates unless equivalence is directly proven.

Do not require a particular MCP, IDE, gopls, code graph, or third-party tool.

## Completion
Zero changes is valid. Report scope, applied changes by pass, behavior-sensitive checks, skipped candidates, exact verification and limitations. Lines removed and complexity-score reduction are not primary success metrics.
