# Comparative and Ablation Benchmark

Use the same fixture corpus, model snapshot, reasoning effort, fixture order, repository context, and tool permissions for every variant. Repeat runs when model variance can affect the conclusion.

## Comparators

Compare:
1. full `go-code-simplifier`;
2. minimal prompt: simplify this Go code without changing observable behavior;
3. Anthropic-style code-simplifier guidance;
4. Compound Engineering-style simplify-code guidance.

Do not copy conclusions or rankings from another skill. Score actual outputs with `scoring.md`.

## Ablations

Remove one instruction group at a time from the full skill:
- Pass 6 strict equivalence audit;
- Go-specific equivalence references;
- Safety Gate;
- pass completion criteria;
- `style-sources.md`;
- `review-efficiency.md`;
- tooling policy;
- broad-scope reviewer guidance.

An ablation is removable only when representative repeated runs show no material regression in unsafe acceptance, safe precision, safe recall, trap rejection, ambiguous restraint, or unnecessary edits, while reducing context/tool/runtime cost.

## Efficiency

Record when available:
- initial skill/reference context tokens;
- total input and output tokens;
- reference files loaded;
- tool calls;
- verification commands;
- runtime.

Compare safety metrics first. Optimize efficiency only among variants with equivalent safety and acceptable recall.

## Release gate

Do not claim benchmarked accuracy or efficiency until the benchmark has actually run. A fixture compiling or its oracle being well-designed is not a model/skill accuracy result.
