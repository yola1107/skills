# Running the A/B benchmark

The deterministic Go fixture checks are the safety floor:

```bash
bash scripts/validate-go-code-simplifier-evals.sh
```

For paired `with_skill` / `without_skill` model evaluation, this repository also provides `evals/evals.json` in the agentskills.io-compatible shape used by `@agilelab/agent-skills-eval`.

From the repository root, with a supported model backend configured:

```bash
npx @agilelab/agent-skills-eval@0.2.1 . \
  --target <target-model> \
  --judge <judge-model> \
  --baseline \
  --strict
```

Use the generated benchmark/report for A/B lift, but apply `scoring.md` to safety decisions. LLM-judge pass rate does not override deterministic Go tests, forbidden edits, or the unsafe-acceptance gate.

For reproducible comparisons, keep model snapshot, reasoning effort, tool permissions, fixture order, and run mode fixed. Repeat representative runs before claiming a lift.
