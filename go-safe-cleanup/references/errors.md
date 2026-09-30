# Error Equivalence

Preserve nil/non-nil, concrete/sentinel identity, errors.Is/errors.As reachability, wrapping tree, error precedence, partial-result-plus-error, and externally consumed codes/messages.

Do not automatically replace equality with errors.Is, add/remove %w wrapping, add logging, convert panic/error contracts, or merge branches because text looks similar. Error-message style is only a candidate; changing an observed message is behavior change.
