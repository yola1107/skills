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

Prefer diagnostics in read-only/non-fixing mode:

- `go test`
- `go test -race` when concurrency-sensitive
- `go vet`
- `go build`
- `staticcheck` when configured/available
- `golangci-lint run` when configured/available
- `gocyclo` / `gocognit` as hotspot signals
- gopls diagnostics/references/rename support when available
- dead-code/callgraph tools as evidence, never sole proof

Diagnostics identify candidates or regressions. They do not authorize behavior changes.

## Mutating tools

Treat tools/actions that rewrite source as code changes, including:

- `go fix`
- `gofmt -r` / `gofmt -s -w`
- `goimports -w`
- gci write/fix modes
- `golangci-lint --fix`
- gopls rename/inline/extract/code actions
- gopatch, eg, SuggestedFixes, custom AST/analysis fixers

Use a mutating tool only for an already-approved cleanup or a narrowly reviewed mechanical batch. Inspect its diff afterward. The generated diff must pass the same Safety Gate, strict equivalence audit, and verification as a hand edit.

Never run a broad fixer merely because a newer Go toolchain offers it. Modernization and dependency migration are separate tasks.

## Renames

For multi-file/private symbol renames, prefer type-aware tooling such as gopls when available over textual replacement. Still inspect the resulting references and diff. A successful rename action proves syntactic/type consistency, not external compatibility or reflection/string-based behavior.

Never use sed/perl/global text replacement for structural Go renames.

## Version awareness

Do not introduce APIs, syntax, fixers, or assumptions newer than the repository's declared Go version. Tool behavior itself can change across Go releases; repository version and CI environment govern.

## Verification effort

Keep effort proportional:
- formatting/local naming: formatter plus narrow compile/test when needed;
- expression/control-flow cleanup: affected package tests and diagnostics;
- structural/shared code: wider dependent tests/build;
- concurrency/external-contract changes: strict audit plus relevant race/integration evidence.

Do not repeatedly rerun broad suites after reversible low-risk edits unless later changes invalidate prior evidence.
