# Comparative Benchmark

Run the same corpus under equivalent model, reasoning effort, repository context and tool permissions with:

1. this `go-code-simplifier`;
2. Anthropic `code-simplifier` guidance;
3. Compound Engineering `ce-simplify-code` guidance;
4. a minimal baseline: simplify this Go code without changing behavior.

Also run ablations when changing the skill:
- without Pass 6 strict equivalence audit;
- without Go-specific equivalence rules;
- without Safety Gate;
- without pass-specific references.

Compare unsafe acceptance first, then ambiguous action, safe precision/recall, unnecessary edits, runtime/tool calls/tokens. Repeat representative runs before drawing conclusions.

Do not copy another skill's ranking or conclusions into this benchmark. The corpus and scoring decide.
