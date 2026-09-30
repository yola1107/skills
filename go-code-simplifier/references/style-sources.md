# External Style Sources

Use external Go style guides and community skills only to discover simplification candidates. They do not define safety or authorize edits.

Useful sources include:
- Go conventions and standard tooling;
- Uber Go Style Guide;
- samber/cc-skills-golang, especially naming, code-style, refactoring, and safety guidance.

Useful candidate heuristics include:
- short readable names and name length matched to scope;
- anti-stutter and consistent concept names;
- reduced nesting and unnecessary `else`;
- small independently verifiable transforms;
- ownership awareness;
- tool-assisted rename/inline when available;
- avoiding premature or weak abstractions.

For every candidate, return to `safety-gate.md` and the relevant pass reference before editing. A source's `MUST`, preferred style, modernization advice, performance advice, or API-design recommendation is not permission to change established behavior.

Repository-local rules take precedence over these sources.


## Rules that are design guidance, not automatic cleanup

Do not mechanically import external `MUST` rules into existing code. In particular:
- “slices/maps must never be nil” can change observable nil/JSON behavior;
- “enum zero must be Unknown/Invalid” can renumber or redefine existing contracts;
- “functions over N parameters need an options struct” changes signatures/APIs;
- “all booleans need is/has/can” can rename fields/methods and break compatibility;
- “prefer value/pointer based on size” can change method/function semantics and nil behavior;
- “replace explicit values with iota” can change external numeric contracts and future insertion behavior;
- modernization such as newer stdlib APIs, dependency removal, or `go fix` belongs to a separate task;
- performance advice such as preallocation, copying, caching, or parallelism is not strict cleanup.

Safe ideas such as receiver naming, MixedCaps, anti-stutter, scope-based local naming, and unnecessary-else removal still require repository fit and the Safety Gate before editing existing code.
