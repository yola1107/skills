# Go Equivalence Rules

Use this reference during the strict equivalence audit and whenever a candidate touches Go semantics that can make a seemingly local rewrite observable.

## Interfaces and typed nil
An interface containing a typed nil pointer can be non-nil. Check interface conversions, direct-return collapses, type assertions, pointer-to-interface changes, receiver changes, and method sets.

## Errors
Preserve:
- nil/non-nil state;
- concrete/sentinel identity;
- `errors.Is` / `errors.As` reachability;
- wrapping tree and `%w` versus `%v`;
- error precedence when multiple conditions fail;
- partial result plus error;
- externally consumed codes/messages where applicable.

Do not automatically replace equality with `errors.Is`, add/remove wrapping, add logging, convert panic/error contracts, or merge branches merely because error text looks similar.

## Slices and maps
Preserve observable nil versus allocated-empty state, map missing versus present-zero, slice backing-array sharing, relevant len/cap, append reuse, subslice lifetime, copy versus alias, ordering, and duplicates.

## Structs, receivers, and copies
Pointer/value receiver changes can alter mutation and method sets. Do not copy mutex, WaitGroup, Once, atomic/no-copy, or ownership-bearing values unless explicitly safe.

## Evaluation and control flow
Preserve call count, argument evaluation effects, short-circuiting, independent versus exclusive branches, loop-control scope, validation/error priority, and panic/recover boundaries.

## defer, resources, panic/recover
Check cleanup timing, LIFO order, captured variable versus evaluated argument, named-return mutation, resource/lock duration, and recover function boundary. Extracting code into a helper can make its defers execute earlier.

## Strings and numbers
Preserve byte versus rune semantics, indexing units, conversions, integer truncation/overflow, floating-point behavior, and externally observable formatting.

## Time and randomness
Preserve observable time-read placement, timeout/timer scope, random source/seed/call count/consumption order when determinism matters.

## Initialization and hidden references
Direct-call search is insufficient for `init`, package initialization, blank imports, registries, reflection, generated code, build tags/platform files, templates, or string-based registration.

## Go version
Judge loop variables, APIs, language behavior, and tooling using repository-declared Go constraints, not assumptions from a newer local toolchain.

Passing tests and direct-reference search are evidence, not complete proof for reflection, registration, external contracts, or concurrency.
