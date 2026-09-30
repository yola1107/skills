# Mechanical Cleanup

This pass owns statement/expression-level redundancy. Function/helper/wrapper restructuring belongs to `local-structure-redundancy.md`.

## Good candidates
- redundant return locals when return type/interface/nil semantics remain identical;
- forwarding locals that add no semantic or evaluation value;
- boolean-return boilerplate;
- identity formatting/conversion with identical semantics;
- redundant syntax or expression noise that can be proven locally;
- non-doc comments that only restate obvious local syntax.

Preserve Go doc comments for exported/package declarations unless documentation cleanup is explicitly in scope. Keep comments that explain reasons, contracts, invariants, ownership, concurrency, protocol/compatibility behavior, workarounds, generated markers, licenses, or compiler/tool directives.

## Intermediate variables
“Used once” is not a deletion rule.

Keep a variable when it:
- names a domain concept or state transition;
- fixes a time/random/external-read evaluation point;
- prevents duplicate side effects;
- documents ownership or a meaningful type boundary;
- is captured by closure/defer;
- materially improves debugging/readability.

Before collapsing expressions check argument evaluation, short-circuiting, typed-nil/interface conversion, conversions, method dispatch, map/slice aliasing, panic behavior, and call count.
