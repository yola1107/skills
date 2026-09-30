# Mechanical Cleanup

Good candidates include redundant return locals, forwarding locals that add no meaning, boolean-return boilerplate, identity formatting/conversion with identical semantics, and proven no-op private wrappers/noise.

Keep an intermediate variable when it names a domain concept/state transition, fixes time/random/external-read evaluation, prevents duplicate side effects, documents ownership/type conversion, is captured by closure/defer, or materially improves debugging/readability.

“Used once” is not a deletion rule.

Before collapsing expressions check argument evaluation, short-circuiting, typed-nil/interface conversion, conversions, dispatch, map/slice aliasing, panic behavior and call count.
