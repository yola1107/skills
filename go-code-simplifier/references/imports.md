# Import Rules

Import cleanup is subordinate to behavior equivalence. Imports normally follow approved code changes; do not turn import cleanup into dependency migration or modernization.

## Grouping policy

First follow repository-local import policy and formatter configuration.

When the repository does not define an import grouping policy, use three semantic groups separated by one blank line:

1. **Go standard library**
2. **Current project/module packages**
3. **Third-party dependencies**

Example:
```go
import (
    "context"
    "errors"
    "time"

    "example.com/project/internal/session"
    "example.com/project/pkg/codec"

    "github.com/google/uuid"
    "go.uber.org/zap"
)
```

Within each group, use repository formatter/tooling order; otherwise normal Go lexical ordering.

## Identify project imports
Resolve local/project grouping in this order:
1. repository formatter configuration (for example gci sections/prefix or goimports local prefixes);
2. repository AGENTS.md/development/style documentation;
3. owning `go.mod` module path;
4. relevant local modules from `go.work` / nested `go.mod`.

Do not hard-code a universal project prefix.

## Allowed cleanup
- remove ordinary imports made unused by an approved cleanup;
- add ordinary imports required by an approved cleanup;
- reorder/format imports to repository policy or the default three-group policy;
- remove a redundant explicit alias identical to the package declaration name when no ambiguity is introduced;
- preserve meaningful aliases for collisions, domains, or versions.

Prefer repository-configured formatting such as `golangci-lint fmt`, gci, goimports, or gofmt when available.

## Aliases
Default to the package declaration name. Named aliases are justified for actual collisions, protocol/domain distinction, versions, or other real ambiguity. A `/vN` import-path suffix alone does not require an alias if the package declaration is already clear.

Alias changes must not introduce shadowing or broken references.

## Behavior-sensitive imports

### Blank imports
`_ "pkg"` may exist solely for initialization/registration. Never remove one merely because no identifier references it. Skip removal unless its side effect is explicitly proven unnecessary and within scope.

### Dot imports
Existing dot imports are report-only by default. Do not rewrite solely for style; broad identifier/shadowing changes may result.

### Build/platform/generated files
Respect build constraints, generated files, and platform-specific source sets.

## Dependency boundary
Do not introduce a new third-party dependency merely to shorten local code, replace one library with another because APIs look similar, migrate functionality between third-party and standard library incidentally, or change the dependency graph via upgrade/tidy unless explicitly required and authorized.

## Tooling
`gofmt` is the baseline formatter. `goimports` may add/remove imports, so review its diff. `gci` is appropriate when repository configuration defines semantic groups. Repository configuration wins over invented CLI flags.

## Verification
After import changes, inspect the import diff (especially blank/dot/alias changes), run repository formatting on touched files, and perform affected-package/build/lint checks required by repository rules.

Import grouping is readability. Import side effects and dependency selection are behavior.
