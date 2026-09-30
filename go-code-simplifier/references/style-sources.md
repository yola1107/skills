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
