# Repository Instructions

This repository contains reusable agent skills. Keep skills small, composable, evidence-driven, and safe to use across repositories.

## Source of truth

For each skill:
- `SKILL.md` owns invocation, precedence, workflow, and completion behavior.
- `references/` owns detailed domain rules. Give each rule one primary owner; cross-reference instead of duplicating it.
- `evals/` owns behavioral or decision-quality regression cases. A rule that guards a known failure mode should have an eval when practical.

Repository-local instructions override external/community skill guidance. External skills and style guides are candidate sources, not automatic authority.

## Change discipline

Before changing a skill:
1. Pin the review base and inspect the diff from that base.
2. State the intended behavior/spec of the skill change.
3. Identify existing references/evals that already own the concern.
4. Prefer editing an existing owner over adding another overlapping rule.

After changing a skill:
1. Review the diff against two independent axes:
   - **Standards:** repository instructions, skill structure, no duplicate/conflicting ownership, concise/composable guidance.
   - **Spec:** the requested behavior is implemented without scope creep or weakening safety.
2. For behavior-sensitive changes, run or extend relevant evals.
3. Re-read the final `SKILL.md` plus touched references for contradictions and stale links.
4. Report checks actually run; do not imply unrun eval/model benchmarks passed.

For broad changes, use independent read-only reviewers for Standards and Spec when the harness supports it. Keep apply/revert decisions with the main agent.

## Skill writing

- Put trigger language and task boundaries in frontmatter description.
- Keep the main skill focused on orchestration; move conditional detail to references.
- Prefer explicit precedence and stop conditions over repeated warnings.
- Avoid model-specific dependencies unless the skill is intentionally model-specific.
- Use risk-adaptive effort: focused changes should not trigger repository-wide scans or broad test suites without evidence.
- Never require a personal IDE, MCP, code graph, or optional local tool unless the skill's purpose specifically depends on it.

## Safety

Do not let style, brevity, modernization, performance, or automated fixer output override a skill's stated safety/behavior contract.

Never weaken tests, lint rules, expected behavior, or verification scope merely to make a skill change appear successful.
