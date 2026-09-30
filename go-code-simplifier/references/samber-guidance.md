# Samber cc-skills-golang Guidance

Use samber/cc-skills-golang as candidate-generation guidance, especially golang-naming, golang-code-style, golang-refactoring and golang-safety.

Adopt these ideas:
- short readable Go names; name length follows scope;
- anti-stutter and consistent concept names;
- understand → safety net → small transform → verify;
- reduce nesting/unnecessary else when semantics stay identical;
- prefer tool-assisted rename/inline when available;
- audit typed nil, slice aliasing, defer/resource and numeric semantics;
- small independently verifiable batches.

Do not import “MUST” style rules blindly. In particular, never automatically initialize all nil slices/maps, redesign functions above a parameter threshold, add defensive copies, rewrite errors, change zero-value/enums, unexport APIs, or modernize syntax if that can change established behavior.

Community style rules are subordinate to this skill's Safety Gate.
