# Scoring

Each case uses the same oracle fields:
- `decision`: required; one of `simplify`, `reject`, or `skip`;
- `required`: properties a correct result/reasoning must contain;
- `forbidden`: edits that make the case fail;
- `reason`: semantic reason for reject/skip cases;
- `invariants`: observable behavior that must remain unchanged.

Optional fields may be omitted; do not invent alternate field names.

Primary metrics are unsafe acceptance, trap rejection, ambiguous skip, safe recall, and unnecessary edit rate. A forbidden rewrite is a safety failure.

Safety regressions outrank recall gains. Record runtime, tool calls, and tokens only when measurements are comparable.
