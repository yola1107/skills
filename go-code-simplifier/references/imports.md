# Import Rules

Import cleanup is subordinate to behavior equivalence. Imports normally follow approved code changes; do not turn import cleanup into dependency migration or modernization.

## Canonical grouping

For hand-written Go code, organize imports into exactly three semantic groups, separated by one blank line:

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

Within each group, use the repository formatter/tooling order; otherwise use normal Go lexical ordering.

## How to identify the project group

Do not hard-code a universal project prefix.

Resolve the project/local group in this order:

1. repository-local formatter configuration (for example gci sections/prefix or goimports local-prefixes);
2. repository-local AGENTS.md or development/style documentation;
3. the owning `go.mod` module path;
4. for a multi-module workspace, the relevant local module paths from `go.work` / nested `go.mod` files.

If repository configuration intentionally defines a different grouping policy, repository policy wins.

For example, a repository configured with:

```yaml
gci:
  sections:
    - standard
    - prefix(yola)
    - default
  custom-order: true
```

means standard library → imports matching `yola` → remaining third-party imports.

## Allowed automatic cleanup

- remove ordinary imports that became unused because of an approved cleanup;
- add an ordinary import required by an approved cleanup;
- format/reorder imports to the repository's configured three-group policy;
- remove a redundant explicit alias when it is identical to the package declaration name and no ambiguity is introduced;
- preserve meaningful aliases used for collisions, domains, or versions.

Prefer the repository's configured formatter, such as `golangci-lint fmt`, gci, goimports, or gofmt. Do not assume a formatter is installed merely because this reference mentions it.

## Aliases

Default to the package declaration name.

A named alias is justified when it:
- resolves an actual name collision;
- distinguishes protocol/domain packages;
- distinguishes versions or otherwise prevents ambiguity.

Do not keep an alias merely because an import path ends in `/vN` when the package declaration name is already clear.

Alias changes must not introduce shadowing or change references. Check local identifiers, package names, interfaces, generated code, reflection/string references where relevant.

## Behavior-sensitive imports

### Blank imports

`_ "pkg"` may exist solely for package initialization, driver/plugin/codec/handler registration, metrics, pprof, or other side effects.

Never remove a blank import merely because no identifier references it. Treat removal as behavior-sensitive and skip unless the initialization effect is explicitly proven unnecessary and within scope.

### Dot imports

Existing dot imports are report-only by default. Do not rewrite them solely for style; doing so can create broad identifier/shadowing changes. Test-framework dot imports are especially likely to be deliberate.

### Build-tag/platform/generated imports

Do not infer unused behavior across build constraints. Respect generated files and platform-specific source sets.

## Dependency boundary

Do not:
- introduce a new third-party dependency merely to make local code shorter;
- replace one package/library with another because APIs look similar;
- migrate third-party functionality to/from the standard library as incidental cleanup;
- run dependency upgrades/tidy that change the dependency graph unless explicitly required and authorized.

A package migration is a separate task even when the resulting import block looks simpler.

## gofmt, goimports, and gci

- `gofmt` is the baseline Go formatter and may be applied to touched files.
- `goimports` may add/remove imports; review its diff rather than treating it as equivalence proof.
- `gci` is appropriate when repository configuration defines semantic import groups.
- If the repository already configures import formatting, use that configuration rather than inventing CLI flags or a competing local convention.

## Verification

After import changes:

1. inspect the import diff, especially blank/dot/alias changes;
2. run the repository formatter on touched files;
3. build/test the affected package as required by repository rules;
4. run configured lint/format checks when applicable.

Import grouping is a readability rule. Import side effects and dependency selection are behavior.
