# External Style Sources

External Go style guides and community skills are candidate sources, not authorities over established behavior.

Useful sources include:
- Go conventions and standard tooling;
- Uber Go Style Guide;
- samber/cc-skills-golang, especially naming, code-style, refactoring, and safety guidance.

Useful candidate heuristics include short readable names, scope-based naming, anti-stutter, reduced nesting, small verifiable transforms, ownership awareness, and tool-assisted rename/inline when available.

## Never import style rules mechanically
Do not automatically:
- normalize nil collections to empty values;
- add/remove defensive copies;
- redesign functions because of a parameter-count threshold;
- add/remove error wrapping/logging;
- change pointer/value receivers or zero-value semantics;
- alter mutex/defer/goroutine/context/lifecycle behavior;
- unexport or rename public APIs;
- preallocate/cache/batch/parallelize for performance;
- modernize syntax/dependencies merely because a guide prefers it.

Repository rules and the Safety Gate always win.
