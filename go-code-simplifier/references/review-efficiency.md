# Review and Efficiency

Load this reference only for broad cleanup scopes or when deciding whether independent reviewers are worth their cost.

## Review axes

For broad scopes, independent read-only reviewers may run in parallel when the harness supports them:

- **Standards:** repository rules, this skill's cleanup rules, and applicable Go conventions.
- **Behavior/spec:** requested cleanup scope, scope creep, and observable-behavior preservation.

Keep the axes separate so style compliance cannot mask a behavior/spec failure. Reviewers do not concurrently edit overlapping code. The main agent owns apply/revert decisions and final verification.

Focused/local cleanup stays single-agent unless a specific unresolved risk justifies another reviewer.

## Effort calibration

Use the smallest context and verification that can establish the required confidence.

- low-risk formatting, import organization, and local naming use narrow references/checks;
- expression/control-flow changes load the relevant Go-semantic rules and affected-package evidence;
- structural/shared changes earn wider reference mapping and dependent checks;
- concurrency, lifecycle, and external-contract surfaces earn strict audit plus relevant specialized evidence.

Once required checks pass, broaden or repeat them only after later edits, failures, or unresolved risks invalidate the prior evidence.

Efficiency/performance findings are separate work unless they are directly behavior-equivalent cleanup. Prefer direct, explicit Go; do not introduce reflection, unsafe, complex generic machinery, callback layers, or dynamic abstractions merely to shorten code.
