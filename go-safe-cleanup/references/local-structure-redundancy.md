# Local Structure and Redundancy

Before removing/inlining a private helper ask whether it provides business naming, validation/policy, synchronization, ownership/resource boundary, instrumentation, compatibility, useful test seam, or a stable abstraction hiding complexity. If none apply and it only forwards, it is an inline candidate. A short function is not redundant merely because it is short.

Consolidate only semantic duplication: same responsibility, errors, side effects, ordering and evolution direction. Skip consolidation requiring mode flags, generic frameworks, callbacks/options that hide flow, or out-of-scope edits.

Extract only coherent responsibilities. Do not split into step1/step2/step3 merely to lower function length or complexity. Do not redesign signatures solely because a style guide sets a parameter threshold.

gocyclo/gocognit locate hotspots; they are not acceptance criteria.
