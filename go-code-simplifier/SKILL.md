---
name: go-code-simplifier
description: Safety-first simplification of existing Golang code. Reduce local redundancy, naming noise, data-flow complexity, nesting, and shallow abstractions only when observable behavior remains equivalent. Do not use for bug fixes, performance redesign, API/protocol/config/schema changes, dependency migration, or concurrency/lifecycle redesign.
---

# Go Code Simplifier

Simplify existing Go code with one non-negotiable rule:

> **Behavior equivalence comes first. If equivalence cannot be established, do not change the code.**

Use this decision priority for every candidate:

> **Safety / behavior equivalence > clarity > simplicity > brevity.**

Never trade an explicit safety check, meaningful boundary, or readable control flow for fewer lines. Optimize for lower cognitive load, clearer local flow, less redundancy, and fewer unnecessary concepts. Fewer lines, functions, or complexity points are not goals by themselves.

## Skill boundary

For behavior-preserving simplification, this skill supersedes overlapping style/refactoring advice from `samber/cc-skills-golang@golang-naming`, `samber/cc-skills-golang@golang-code-style`, and `samber/cc-skills-golang@golang-refactoring`. Those skills may help discover candidates, but they do not authorize edits that fail this skill's Safety Gate. This skill does not supersede domain-specific skills for debugging, performance, security, databases, protocols, or framework APIs.

## Precedence

1. User scope and explicit constraints.
2. Repository-local rules and established contracts.
3. This skill's safety and behavior-equivalence rules.
4. Go semantics for the repository's declared version.
5. External style guidance only as candidate sources.

Always read `references/safety-gate.md` and `references/verification.md`. Read `references/tooling.md` when choosing or running Go tooling. Read `references/constants-types.md` whenever a candidate touches constants, enum-like declarations, declaration forms, or explicit numeric conversions. Load other pass-specific and behavior-sensitive references only when relevant.

## Hard boundary

Do not mix cleanup with bug fixes, new validation, retries, caching, batching, performance redesign, API/protocol/config/schema changes, dependency upgrades/migration, or concurrency/lifecycle redesign. Report them separately unless scope is explicitly expanded.

Treat pre-existing worktree changes as protected. The cleanup baseline is the actual state at cleanup start, not necessarily `HEAD`. Reading may extend beyond mutation scope to prove behavior; editing may not silently extend beyond it.

## Workflow

### Pass 0 — Scope & Baseline
Resolve mutation scope, repository guidance, worktree/staged changes, Go module/workspace boundaries, and baseline checks. Record pre-existing failures. Classify the task risk/size so later reference loading and verification stay proportional. Do not edit production code.

### Pass 1 — Understand & Candidate Map
Read enough callers, callees, interfaces, tests, registrations, ownership and external contracts to understand current behavior and identify worthwhile simplification candidates. When external style guidance would help discover candidates, load `references/style-sources.md`; it never overrides repository rules or the Safety Gate.

If evidence is insufficient for a behavior-sensitive candidate, prefer skipping it. Add characterization tests only when the cleanup has meaningful value, tests are within authorized mutation scope, and the tests record existing behavior rather than redefine it.

Before editing, summarize the intended cleanup batch and flag any behavior-sensitive areas it touches (for example errors, concurrency, lifecycle, external contracts, reflection/registration, ownership, or serialization). Do not edit production logic in this pass.

### Pass 2 — Mechanical & Local Cleanup
Load:
- `references/formatting-whitespace.md`
- `references/imports.md`
- `references/mechanical-cleanup.md`

Apply formatting/whitespace, import organization, and statement/expression-level mechanical cleanup. Do not perform function/helper restructuring in this pass. Verify each coherent batch according to `references/verification.md`.

### Pass 3 — Naming & Local Data Flow
Load `references/naming-local-data-flow.md`. Improve local/private naming, reduce scope, and make state transitions clearer. Pass 2 owns decisions about purely redundant intermediate variables. Exported renames are report-only by default. Verify each coherent batch.

### Pass 4 — Control Flow
Load `references/control-flow.md`. Reduce unnecessary nesting and clarify guards/branches only when evaluation order, call count, error precedence, mutations and side effects remain equivalent. Verify each coherent batch.

### Pass 5 — Structure & Duplication
Load `references/local-structure-redundancy.md`. Remove only proven shallow private helpers/wrappers and semantic duplication. Preserve useful business naming, synchronization, ownership, validation, instrumentation, compatibility and test seams. Verify each coherent batch.

### Pass 6 — Strict Equivalence Audit
Stop simplifying. Review the complete cleanup diff against the cleanup baseline. Load `references/go-equivalence-rules.md` and, when relevant, `references/concurrency-lifecycle.md` and `references/external-contracts.md`. Prove equivalence for suspicious changes or revert the individual cleanup.

### Pass 7 — Final Verification
Run final verification according to `references/verification.md`. Claims must match checks actually run on the final relevant state.

## Reviewer strategy

Default to one agent for focused/local cleanup. For broad scopes where independent read-only scans can save time or improve coverage, delegate reviewers in parallel when the harness supports it. Keep review axes independent:
- **Standards:** repository rules plus this skill's cleanup rules and Go conventions;
- **Behavior/spec:** requested cleanup scope plus observable-behavior preservation.

Do not let reviewers concurrently edit overlapping code, and do not merge the two axes into one vague verdict. Final verification and apply/revert decisions remain the main agent's responsibility.

Efficiency findings are separate optimization candidates unless behavior equivalence is directly established. Do not introduce reflection, unsafe, complex generics/type machinery, higher-order callback layers, or new closure-heavy/dynamic abstractions merely to make code shorter or more "elegant"; prefer direct, explicit Go.

Do not require a particular MCP, IDE, `gopls`, code graph, or third-party tool. Use available tools opportunistically.

## Efficiency discipline

Use risk-adaptive effort. Low-risk formatting/naming/import-only batches should load only relevant references and use narrow verification. Structural or behavior-sensitive changes require the strict audit and broader evidence. Do not write implementation-mirroring tests for reversible low-impact edits. Once required checks pass, broaden or repeat them only when later edits, failures, or unresolved risks justify it.

## Completion

Zero production-code changes is valid. Report scope, applied changes by pass, behavior-sensitive/risk areas reviewed, skipped candidates, exact verification performed, and limitations. Call out explicitly when the cleanup touched concurrency/lifecycle, public or external contracts, reflection/registration, ownership/aliasing, serialization, or error identity/wrapping. Do not use lines removed or complexity-score reduction as primary success metrics.
