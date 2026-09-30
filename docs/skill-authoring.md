# Skill Authoring Standards

Use these standards when creating or editing a skill in this repository.

## Ownership

- `SKILL.md` owns invocation, precedence, ordered workflow, reference routing, and completion criteria.
- `references/` owns detailed rules. Each meaning has one primary owner; other files point to it instead of restating it.
- `evals/` owns decision-quality and behavioral regressions for known failure modes.

External/community skills and style guides are candidate sources. Repository rules and the target skill's safety contract decide what is adopted.

## Change workflow

Before editing:
1. Pin the review base and inspect the diff.
2. State the requested behavior/spec.
3. Locate the existing owner for each concern.
4. Extend an owner before creating another overlapping rule.

After editing:
1. Review **Standards**: repository instructions, ownership, progressive disclosure, concise pointers, stale links, duplication/no-ops.
2. Review **Spec** independently: requested behavior, scope creep, and safety-contract regressions.
3. Run or extend relevant evals for behavior-sensitive changes.
4. Re-read the final `SKILL.md` and touched references.
5. Report only checks actually run.

For broad changes, independent read-only Standards and Spec reviewers may run in parallel. The main agent owns apply/revert decisions.

## Writing for agents

Keep always-loaded text small. Put only navigation and high-value steering in `AGENTS.md`. Put ordered actions in the main skill; disclose branch-specific rules behind precise pointers that say when to read them.

Give every step a checkable completion criterion. Prefer positive target behavior; reserve prohibitions for hard safety boundaries. Delete no-op instructions and stale caches of facts that the repository/tooling can reveal directly.

Descriptions for model-invoked skills are context pointers: name the distinct trigger branches and task boundary without duplicating the body.

Use risk-adaptive effort. Focused edits use focused context and checks; broad or behavior-sensitive changes earn broader review and verification.

## Safety

A skill's declared safety/behavior contract outranks style, brevity, modernization, performance advice, and automated fixer output. Never weaken tests, lint rules, expected behavior, or verification scope to make a change pass.
