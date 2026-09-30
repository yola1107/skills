# External Style Sources

Use external Go style guides and community skills as candidate sources only. Repository rules and this skill's Safety Gate decide whether an existing-code change is allowed.

Relevant sources include Go conventions, the Uber Go Style Guide, and samber/cc-skills-golang naming/code-style/refactoring/safety guidance. Candidate mechanics belong to the matching pass reference; do not duplicate them here.

## Filter design guidance from cleanup

Treat external `MUST` rules as design guidance when applying them would change established behavior or contracts. Common examples:

- forcing nil slices/maps to allocated-empty values can change nil/JSON behavior;
- adding an Unknown/Invalid enum zero can renumber or redefine contracts;
- replacing larger signatures with options structs changes APIs;
- renaming boolean fields/methods can break source or reflection contracts;
- changing pointer/value choices can alter mutation, method sets, nil behavior, or copying;
- replacing explicit numeric constants with `iota` can change external values and insertion semantics;
- newer stdlib APIs, dependency removal, or automated modernization belong to separate modernization work;
- preallocation, copying, caching, batching, or parallelism belong to performance work.

When an external rule only identifies a candidate, route it to the owning pass reference and re-run the Safety Gate before editing.
