---
name: go-code-simplifier
description: Simplify or clean up existing Golang code while preserving observable behavior. Use for behavior-preserving cleanup of redundancy, local naming/data flow, control flow, imports/formatting, constants, and shallow private abstractions. Route bug fixes, performance or modernization work, API/protocol/config/schema changes, dependency migration, and concurrency/lifecycle redesign to separate work.
---

# Go Code Simplifier

Every candidate follows one decision order:

> **Safety / behavior equivalence > clarity > simplicity > brevity.**

When equivalence is unproven, preserve the existing code. Keep explicit safety checks, meaningful boundaries, and readable control flow when they carry information. Optimize for lower cognitive load and fewer unnecessary concepts, not fewer lines.

## Skill boundary

For behavior-preserving simplification, this skill supersedes overlapping style/refactoring advice from `samber/cc-skills-golang@golang-naming`, `samber/cc-skills-golang@golang-code-style`, and `samber/cc-skills-golang@golang-refactoring`. Those skills may help discover candidates, but they do not authorize edits that fail this skill's Safety Gate. This skill does not supersede domain-specific skills for debugging, performance, security, databases, protocols, or framework APIs.

## Precedence

1. User scope and explicit constraints.
2. Repository-local rules and established contracts.
3. This skill's safety and behavior-equivalence rules.
4. Go semantics for the repository's declared version.
5. External style guidance only as candidate sources.

Always read `references/safety-gate.md`. Read `references/verification.md` before the first code-changing batch or when deciding what evidence is required. Read `references/tooling.md` before choosing a nontrivial or source-mutating Go tool. Read `references/constants-types.md` when a candidate touches constants, enum-like declarations, declaration forms, or explicit numeric conversions. Load other references only when their branch is reached.

## Scope boundary

This skill owns behavior-preserving cleanup. Treat bug fixes, new validation, retries, caching/batching, performance or modernization work, API/protocol/config/schema changes, dependency upgrades/migration, and concurrency/lifecycle redesign as separate work unless the user explicitly expands scope.

Treat pre-existing worktree changes as protected. The cleanup baseline is the actual state at cleanup start, not necessarily `HEAD`. Reading may extend beyond mutation scope to prove behavior; editing may not silently extend beyond it.

## Workflow

### Pass 0 — Scope & Baseline
Resolve mutation scope, repository guidance, worktree/staged changes, Go module/workspace boundaries, and baseline checks. Record pre-existing failures and classify risk/size. **Complete when** mutation scope, baseline, applicable repository rules, and verification entry points are known. Production code remains unchanged.

### Pass 1 — Understand & Candidate Map
Read enough callers, callees, interfaces, tests, registrations, ownership and external contracts to understand current behavior and identify worthwhile simplification candidates. When external style guidance would help discover candidates, load `references/style-sources.md`; it never overrides repository rules or the Safety Gate.

If evidence is insufficient for a behavior-sensitive candidate, prefer skipping it. Add characterization tests only when the cleanup has meaningful value, tests are within authorized mutation scope, and the tests record existing behavior rather than redefine it.

Before editing, summarize the intended cleanup batch and flag behavior-sensitive areas it touches (for example errors, concurrency, lifecycle, external contracts, reflection/registration, ownership, or serialization). **Complete when** every candidate is classified as safe-to-attempt, needs-more-evidence, or skip, with relevant references identified. Production logic remains unchanged.

### Pass 2 — Mechanical & Local Cleanup
Load `references/formatting-whitespace.md` for visual cleanup and `references/mechanical-cleanup.md` for statement/expression cleanup. Load `references/imports.md` only when imports are changed or import organization is in scope.

Apply the relevant formatting, import, and statement/expression cleanup. Function/helper restructuring belongs to Pass 5. **Complete when** all in-scope mechanical candidates are applied or skipped with a reason, and each applied coherent batch has the verification required by `references/verification.md`.

### Pass 3 — Naming & Local Data Flow
Load `references/naming-local-data-flow.md`. Improve local/private naming, reduce scope, and make state transitions clearer. Pass 2 owns purely redundant intermediate-variable removal; exported renames are report-only by default. **Complete when** every in-scope naming/data-flow candidate is applied or skipped and applied batches are verified.

### Pass 4 — Control Flow
Load `references/control-flow.md`. Reduce unnecessary nesting and clarify guards/branches only when evaluation order, call count, error precedence, mutations and side effects remain equivalent. **Complete when** every in-scope control-flow candidate is applied or skipped and applied batches are verified.

### Pass 5 — Structure & Duplication
Load `references/local-structure-redundancy.md`. Remove only proven shallow private helpers/wrappers and semantic duplication while preserving meaningful boundaries. **Complete when** every in-scope structural candidate is applied or skipped and applied batches are verified.

### Pass 6 — Strict Equivalence Audit
Stop simplifying. Review the complete cleanup diff against the baseline. Load `references/go-equivalence-rules.md` and, when relevant, `references/concurrency-lifecycle.md` and `references/external-contracts.md`. **Complete when** every changed behavior-sensitive hunk has equivalence evidence or has been reverted.

### Pass 7 — Final Verification
Run final verification according to `references/verification.md`. **Complete when** required final checks have run on the final relevant state and every reported claim matches observed evidence.

## Review and effort

For focused/local cleanup, stay single-agent and use risk-proportional evidence. For broad scopes, independent review, or uncertainty about review cost, load `references/review-efficiency.md`.

## Completion

Zero production-code changes is valid. Report scope, applied changes by pass, behavior-sensitive/risk areas reviewed, skipped candidates, exact verification performed, and limitations. Call out explicitly when the cleanup touched concurrency/lifecycle, public or external contracts, reflection/registration, ownership/aliasing, serialization, or error identity/wrapping. Do not use lines removed or complexity-score reduction as primary success metrics.
