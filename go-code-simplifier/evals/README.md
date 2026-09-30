# Eval Suite

These fixtures evaluate the decision quality of `go-code-simplifier`.

Three classes:
- **safe** — the simplifier should apply the cleanup;
- **traps** — the simplifier must reject the tempting rewrite;
- **ambiguous** — evidence is intentionally insufficient; the simplifier should skip rather than guess.

Each case contains Go source and `expected.yaml`. The expected decision is the primary oracle. Where practical, Go tests encode observable invariants.

Safety-first target: unsafe acceptance should approach zero. Safe-cleanup recall is secondary.

Run each fixture in isolation with the skill enabled. Record proposed diff/decision, then compare it with `expected.yaml`. For executable fixtures, also run `go test ./...`.

A passing Go test alone does not prove the skill decision is correct; trap and ambiguous cases specifically test whether the agent refuses unsafe or unproven rewrites.


## Oracle quality

Classify a case as a **trap** only when the fixture itself establishes a concrete unsafe rewrite or invariant violation. Prefer an executable test or another deterministic oracle; where possible, verify that the original is green and a known-bad mutation is red.

Use **ambiguous** when the concern is plausible but the fixture does not prove an observable break (for example unknown external contracts, reflection/build-tag callers, or a declaration change whose risk depends on unseen uses). Do not reward blanket conservatism by labeling merely speculative risks as traps.

Materialize each fixture recursively: cases may contain nested local modules or support packages.
