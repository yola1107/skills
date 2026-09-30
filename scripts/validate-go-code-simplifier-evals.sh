#!/usr/bin/env bash
set -euo pipefail

root="${1:-go-code-simplifier/evals}"
fail=0
count=0

while IFS= read -r mod; do
  dir="${mod%/go.mod}"
  case "$dir" in
    */thirdparty/*|*/driver) continue ;;
  esac
  count=$((count + 1))
  echo "::group::go test $dir"
  if ! (cd "$dir" && go test ./...); then
    fail=1
  fi
  echo "::endgroup::"
done < <(find "$root" -name go.mod -type f | sort)

echo "validated $count fixture modules"
exit "$fail"
