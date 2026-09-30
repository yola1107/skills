# Go Tooling Policy

Use repository-native tooling first. Tools support behavior-equivalent cleanup; tool output is not proof of equivalence.

## Discovery order

1. repository AGENTS.md/development documentation;
2. Makefile/Taskfile/scripts/CI commands;
3. formatter/linter configuration such as .golangci.yml;
4. go.mod/go.work and declared Go version;
5. standard Go tools;
6. optional installed third-party diagnostics.

Do not install or require a tool merely because this skill mentions it.

## Low-risk formatting tools

`gofmt` on touched Go files is the default formatter when the repository does not define a stronger formatting workflow.

Repository-configured import formatting such as gci may be used according to `imports.md`.

## Diagnostic tools

Use repository-native checks in read-only/non-fixing mode. Standard examples are `go test`, `go vet`, `go build`, and `go test -race` for concurrency-sensitive paths; configured tools such as staticcheck, golangci-lint, complexity, gopls, dead-code, or callgraph diagnostics may add evidence.

Diagnostics identify candidates or regressions; they do not authorize behavior changes. Let repository scripts/configuration reveal the exact available command instead of reproducing its setup here.

## Mutating tools

Treat any source-rewriting action as a code change, including fixer/write modes (`go fix`, rewrite-mode gofmt/goimports/gci/linters), refactor code actions (for example gopls rename/inline/extract), and bulk rewrite/AST tools.

Use a mutating tool only for an already-approved cleanup or a narrowly reviewed mechanical batch. Inspect its diff afterward. The generated diff must pass the same Safety Gate, strict equivalence audit, and verification as a hand edit.

Never run a broad fixer merely because a newer Go toolchain offers it. Modernization and dependency migration are separate tasks.

## Renames

For multi-file/private symbol renames, prefer type-aware tooling such as gopls when available over textual replacement. Still inspect the resulting references and diff. A successful rename action proves syntactic/type consistency, not external compatibility or reflection/string-based behavior.

Never use sed/perl/global text replacement for structural Go renames.

## Version awareness

Do not introduce APIs, syntax, fixers, or assumptions newer than the repository's declared Go version. Tool behavior itself can change across Go releases; repository version and CI environment govern.

Verification depth and rerun policy are owned by `verification.md`.
