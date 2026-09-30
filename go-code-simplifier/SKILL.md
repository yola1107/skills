---
name: go-code-simplifier
description: Safety-first simplification of existing Go code. Reduce local redundancy, naming noise, data-flow complexity, nesting, and shallow abstractions only when observable behavior remains equivalent. Do not use for bug fixes, performance redesign, API/protocol/config/schema changes, dependency migration, or concurrency/lifecycle redesign.
---

# Go Code Simplifier

Simplify existing Go code with one non-negotiable rule:

> **Behavior equivalence comes first. If equivalence cannot be established, do not change the code.**

Optimize for lower cognitive load, clearer local flow, less redundancy, and fewer unnecessary concepts. Fewer lines, functions, or complexity points are not goals by themselves.

## Precedence

1. User scope and explicit constraints.
2. Repository-local rules and established contracts.
3. This skill's safety and behavior-equivalence rules.
4. Go semantics for the repository's declared version.
5. External style guidance only as candidate sources.

Always read `references/safety-gate.md` and `references/verification.md`. Load pass-specific and behavior-sensitive references only when relevant.

## Hard boundary

Do not mix cleanup with bug fixes, new validation, retries, caching, batching, performance redesign, API/protocol/config/schema changes, dependency upgrades/migration, or concurrency/lifecycle redesign. Report them separately unless scope is explicitly expanded.

Treat pre-existing worktree changes as protected. The cleanup baseline is the actual state at cleanup start, not necessarily `HEAD`. Reading may extend beyond mutation scope to prove behavior; editing may not silently extend beyond it.

## Workflow

### Pass 0 — Scope & Baseline
Resolve mutation scope, repository guidance, worktree/staged changes, Go module/workspace boundaries, and baseline checks. Record pre-existing failures. Do not edit production code.

### Pass 1 — Understand & Candidate Map
Read enough callers, callees, interfaces, tests, registrations, ownership and external contracts to understand current behavior and identify worthwhile simplification candidates.

If evidence is insufficient for a behavior-sensitive candidate, prefer skipping it. Add characterization tests only when the cleanup has meaningful value, tests are within authorized mutation scope, and the tests record existing behavior rather than redefine it.

Do not edit production logic in this pass.

### Pass 2 — Mechanical & Local Cleanup
Load:
- `references/formatting-whitespace.md`
- `references/imports.md`
- `references/mechanical-cleanup.md`

Apply formatting/whitespace, import organization, and statement/expression-level mechanical cleanup. Do not perform function/helper restructuring in this pass. Verify each coherent batch according to `references/verification.md`.

### Pass 3 — Naming & Local Data Flow
Load `references/naming-local-data-flow.md`. Improve local/private naming, remove meaningless intermediates, reduce scope, and make state transitions clearer. Exported renames are report-only by default. Verify each coherent batch.

### Pass 4 — Control Flow
Load `references/control-flow.md`. Reduce unnecessary nesting and clarify guards/branches only when evaluation order, call count, error precedence, mutations and side effects remain equivalent. Verify each coherent batch.

### Pass 5 — Structure & Duplication
Load `references/local-structure-redundancy.md`. Remove only proven shallow private helpers/wrappers and semantic duplication. Preserve useful business naming, synchronization, ownership, validation, instrumentation, compatibility and test seams. Verify each coherent batch.

### Pass 6 — Strict Equivalence Audit
Stop simplifying. Review the complete cleanup diff against the cleanup baseline. Load `references/go-equivalence-rules.md` and, when relevant, `references/concurrency-lifecycle.md` and `references/external-contracts.md`. Prove equivalence for suspicious changes or revert the individual cleanup.

### Pass 7 — Final Verification
Run final verification according to `references/verification.md`. Claims must match checks actually run on the final relevant state.

## Reviewer strategy

Default to one agent. For broad scopes, optional read-only reviewers may separately scan simplification candidates and behavior-equivalence risks. Do not let reviewers concurrently edit overlapping code. Final verification and apply/revert decisions remain the main agent's responsibility.

Efficiency findings are separate optimization candidates unless behavior equivalence is directly established.

Do not require a particular MCP, IDE, `gopls`, code graph, or third-party tool. Use available tools opportunistically.

## Completion

Zero production-code changes is valid. Report scope, applied changes by pass, behavior-sensitive checks, skipped candidates, exact verification performed, and limitations. Do not use lines removed or complexity-score reduction as primary success metrics.
