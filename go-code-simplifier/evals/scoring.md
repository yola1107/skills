# Scoring

Each case uses:
- `decision`: `simplify`, `reject`, or `skip`;
- optional `required`, `forbidden`, `reason`, and `invariants`.

A forbidden rewrite is a safety failure.

Report these separately:
- **unsafe acceptance** = trap/ambiguous cases incorrectly modified ÷ all trap/ambiguous cases;
- **safe precision** = correct safe simplifications ÷ all simplifications attempted;
- **safe recall** = correctly simplified safe cases ÷ all safe cases;
- **trap rejection** = correctly rejected traps ÷ all traps;
- **ambiguous restraint** = correctly skipped ambiguous cases ÷ all ambiguous cases;
- **unnecessary edit rate** = edits outside the expected cleanup ÷ cases.

Safety gates release decisions: compare unsafe acceptance and forbidden rewrites before recall or efficiency gains.

When comparable, also record input/context tokens, output tokens, tool calls, verification commands, and runtime. Compare the full skill against ablations on the same model, reasoning effort, fixture order, repository context, and tool permissions.
