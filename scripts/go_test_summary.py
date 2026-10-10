"""Summarize one go test -json invocation without counting human-readable output.

Python 3.9+, standard library only. This reads logs; it never executes Go.
See https://pkg.go.dev/cmd/test2json for the event format.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Iterable, Optional


RESULT_ACTIONS = {"pass", "fail", "skip", "bench"}
KINDS = ("top_level", "subtests", "examples", "fuzz", "benchmarks", "other")


def test_kind(name: str) -> str:
    root = name.split("/", 1)[0]
    if root.startswith("Benchmark"):
        return "benchmarks"
    if root.startswith("Example"):
        return "examples"
    if root.startswith("Fuzz"):
        return "fuzz"
    if root.startswith("Test"):
        return "subtests" if "/" in name else "top_level"
    return "other"


def _test_record(package: str, package_run: int, name: str, occurrence: int) -> dict:
    """Construct a record; lifecycle and occurrence changes stay at call sites."""
    return {
        "package": package, "package_run": package_run,
        "test": name, "occurrence": occurrence, "kind": test_kind(name),
    }


def summarize(text: str, exit_code: Optional[int], expected_packages: Iterable[str] = ()) -> dict:
    """Count observed result events, retaining failures and unfinished tests.

    complete means the observed stream is internally complete, NOT proof that
    every requested package/test ran. Supply expected_packages when known and
    retain the original command/selectors, stderr, and process exit status.
    """
    if exit_code is not None and type(exit_code) is not int:
        raise ValueError("exit_code must be an integer or None")
    if isinstance(expected_packages, str):
        raise ValueError("expected_packages must be an iterable of package names, not a string")
    expected = set(expected_packages)
    if any(not isinstance(p, str) or not p for p in expected):
        raise ValueError("expected_packages must contain nonempty package names")
    active_packages, active_tests, occurrences = {}, {}, Counter()
    results, package_results, issues, failed_builds = [], [], [], set()
    benchmark_events = []
    package_runs = Counter()

    # JSONL is LF-delimited; Unicode separators inside strings are not records.
    for number, line in enumerate(text.split("\n"), 1):
        if not line.strip(" \t\r"):
            continue
        try:
            event = json.loads(line)
        except (ValueError, RecursionError):
            issues.append(f"line {number}: invalid JSON")
            continue
        if not isinstance(event, dict):
            issues.append(f"line {number}: expected event object")
            continue
        action = event.get("Action")
        if not isinstance(action, str):
            issues.append(f"line {number}: missing action")
            continue
        # Newer Go versions may interleave build events with test events.
        if action in {"build-output", "build-fail"}:
            path = event.get("ImportPath")
            if not isinstance(path, str) or not path:
                issues.append(f"line {number}: build event lacks ImportPath")
            elif action == "build-fail":
                failed_builds.add(path)
            continue
        package, name = event.get("Package"), event.get("Test", "")
        if not isinstance(package, str) or not package or not isinstance(name, str):
            issues.append(f"line {number}: invalid Package or Test")
            continue
        if action == "start" and not name:
            if package in active_packages:
                issues.append(f"line {number}: package restarted before completion: {package}")
            package_runs[package] += 1
            active_packages[package] = package_runs[package]
            continue
        if package not in active_packages:
            issues.append(f"line {number}: event outside package run: {package}")
        key = (package, name)
        if name and test_kind(name) == "benchmarks" and action in RESULT_ACTIONS | {"run"}:
            # Benchmarks may emit run/output without a per-benchmark result.
            # Record only observed events: neither run nor bench counts measurements.
            benchmark_events.append({
                "package": package, "package_run": package_runs[package],
                "test": name, "action": action, "line": number,
            })
            if action in RESULT_ACTIONS:
                occurrences[key] += 1
                record = _test_record(package, package_runs[package], name, occurrences[key])
                results.append({**record, "action": action})
            continue
        if action == "run" and name:
            if key in active_tests:
                issues.append(f"line {number}: test restarted before completion: {package}/{name}")
            occurrences[key] += 1
            active_tests[key] = _test_record(package, package_runs[package], name, occurrences[key])
        elif action in RESULT_ACTIONS and name:
            record = active_tests.pop(key, None)
            if action == "bench" and test_kind(name) != "benchmarks":
                issues.append(f"line {number}: bench result for a non-benchmark: {name}")
            if record is None:
                issues.append(f"line {number}: test result without run: {package}/{name}")
                occurrences[key] += 1
                record = _test_record(package, package_runs[package], name, occurrences[key])
            results.append({**record, "action": action})
        elif action in {"pass", "fail", "skip"} and not name:
            run = active_packages.pop(package, package_runs[package])
            package_results.append({"package": package, "package_run": run, "action": action})
            failed_build = event.get("FailedBuild")
            if isinstance(failed_build, str) and failed_build:
                failed_builds.add(failed_build)
            if action != "fail" and any(
                r["package"] == package and r["package_run"] == run and r["action"] == "fail"
                for r in results
            ):
                issues.append(f"line {number}: non-failing package has failed test: {package}")
        elif action == "output":
            # Output may contain fake PASS/FAIL lines; never use it as a count.
            continue
        elif action in {"pause", "cont"} and name:
            if key not in active_tests:
                issues.append(f"line {number}: pause/cont without run: {package}/{name}")
        else:
            issues.append(f"line {number}: unsupported action or event shape: {action}")

    if text and not text.endswith("\n"):
        issues.append("log lacks final newline; capture may be truncated")
    if not package_results:
        issues.append("no completed package result")
    for package in sorted(active_packages):
        issues.append(f"package lacks terminal event: {package}")
    for package in sorted(expected - {r["package"] for r in package_results}):
        issues.append(f"expected package absent: {package}")
    if active_tests:
        issues.append("tests lack terminal events; inspect crash/timeout output")
    if exit_code is None:
        issues.append("process exit status is unknown")
    counts = {kind: {a: 0 for a in ("pass", "fail", "skip", "bench")} for kind in KINDS}
    counts["packages"] = {a: 0 for a in ("pass", "fail", "skip")}
    for result in results:
        counts[result["kind"]][result["action"]] += 1
    for result in package_results:
        counts["packages"][result["action"]] += 1
    failed = bool(
        (exit_code is not None and exit_code != 0) or failed_builds
        or any(r["action"] == "fail" for r in results + package_results)
    )
    complete = not issues
    successful = sum(counts[k]["pass"] for k in ("top_level", "examples", "fuzz"))
    skipped = any(counts[k]["skip"] for k in KINDS)
    if failed:
        status = "failed"
    elif not complete:
        status = "incomplete"
    elif successful:
        status = "passed_with_skips" if skipped or counts["packages"]["skip"] else "passed"
    else:
        status = "skipped" if skipped else "no_tests"
    return {
        "schema_version": 1, "status": status, "complete": complete, "exit_code": exit_code,
        "counting_unit": "observed result events; benchmark events are not measurement counts",
        "counts": counts, "test_results": results, "package_results": package_results,
        "unfinished_tests": list(active_tests.values()), "build_failures": sorted(failed_builds),
        "benchmark_events": benchmark_events,
        "issues": issues,
    }


def summarize_bytes(raw: bytes, exit_code: Optional[int], expected_packages: Iterable[str] = ()) -> dict:
    """Parse a decoded view without changing the caller's raw evidence bytes."""
    decode_issue = None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        text = raw.decode("utf-8", errors="replace")
        decode_issue = f"stdout is not valid UTF-8 at byte {exc.start}; view uses replacement characters"
    report = summarize(text, exit_code, expected_packages)
    report["stdout_decode_error"] = decode_issue is not None
    if decode_issue:
        report["issues"].append(decode_issue)
        report["complete"] = False
        if report["status"] != "failed":
            report["status"] = "incomplete"
    return report


def _exit_code(value: str) -> Optional[int]:
    if value == "unknown":
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected an integer or 'unknown'") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path, help="complete stdout from ONE go test -json invocation")
    parser.add_argument("--exit-code", type=_exit_code, required=True, help="actual Go status, or unknown if not observed; never tee's")
    parser.add_argument("--expect-package", action="append", default=[], help="expected import path (repeatable)")
    args = parser.parse_args()
    try:
        raw = args.log.read_bytes()
        report = summarize_bytes(raw, args.exit_code, args.expect_package)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"cannot summarize log: {exc}\n")
    report["source"] = {"path": str(args.log.resolve()), "sha256": hashlib.sha256(raw).hexdigest()}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    # A valid summary is not necessarily a successful test run.
    if report["status"] == "failed":
        return 1
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
