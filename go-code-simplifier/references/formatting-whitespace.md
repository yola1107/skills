# Formatting and Whitespace

Prefer gofmt on touched files, removal of trailing whitespace and repeated meaningless blank lines, and Go-tool-produced spacing.

Blank lines communicate semantic grouping. Keep a single blank line when it separates meaningful stages such as validate → compute → publish or setup → execute → cleanup. Remove blank lines that split one continuous statement group without adding meaning; collapse repeated blank lines.

Remove comments that only translate obvious syntax. Keep why-comments, invariants, concurrency/ownership constraints, protocol/compatibility notes, workarounds, generated markers, licenses and directives.

Do not reformat unrelated files or reorder whole files/packages during local cleanup.
