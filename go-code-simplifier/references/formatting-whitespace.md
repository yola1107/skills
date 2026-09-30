# Formatting and Whitespace

This pass handles visual structure only.

Prefer the repository's configured formatter; otherwise use `gofmt` on touched Go files. Remove trailing whitespace and repeated meaningless blank lines.

Blank lines communicate semantic grouping. Keep a single blank line when it separates meaningful stages such as validate → compute → publish or setup → execute → cleanup. Remove blank lines that split one continuous statement group without adding meaning; collapse repeated blank lines.

Do not reformat unrelated files, reorder declarations/files/packages, or perform comment/content cleanup here.
