# Local Structure and Redundancy

This pass owns function/method/helper/wrapper structure and semantic duplication. Statement-level redundancy belongs to `mechanical-cleanup.md`.

## Helper/wrapper test
Before removing or inlining a private helper ask whether it provides:
- business/domain naming;
- validation or policy;
- synchronization;
- ownership/resource boundary;
- instrumentation/observability;
- compatibility;
- useful test seam;
- a stable abstraction hiding complexity.

If none apply and it only forwards, it is an inline candidate. A short function is not redundant merely because it is short.

## Duplication
Consolidate only semantic duplication: same responsibility, errors, side effects, ordering, and likely evolution direction.

Skip consolidation that requires mode flags, generic frameworks, callbacks/options that hide flow, or edits outside mutation scope. A little clear duplication can be cheaper than a weak abstraction.

## Function structure
Extract only coherent responsibilities. Do not split into `step1/step2/step3` merely to lower function length or complexity. Do not redesign signatures solely because a style guide sets a parameter-count threshold.

`gocyclo` / `gocognit` may locate hotspots; they are not acceptance criteria.
