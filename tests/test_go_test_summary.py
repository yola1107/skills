"""Regression tests for result accounting; no model or Go process is involved."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.go_test_summary import summarize


def event(action, package="example/p", test="", **extra):
    return {"Action": action, "Package": package, **({"Test": test} if test else {}), **extra}


def stream(events):
    return "".join(json.dumps(e) + "\n" for e in events)


def passing(package="example/p", name="TestOne"):
    return [event("start", package), event("run", package, name),
            event("pass", package, name), event("pass", package)]


class GoSummaryTests(unittest.TestCase):
    def test_nested_subtests_and_output_are_not_top_level(self):
        events = [event("start"), event("run", test="TestParent"),
                  event("run", test="TestParent/child"),
                  event("run", test="TestParent/child/nested"),
                  event("output", test="TestParent", Output="--- PASS: TestFake\n--- FAIL: TestFake\n"),
                  event("pass", test="TestParent/child/nested"),
                  event("pass", test="TestParent/child"), event("pass", test="TestParent"), event("pass")]
        report = summarize(stream(events), 0)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["counts"]["top_level"]["pass"], 1)
        self.assertEqual(report["counts"]["subtests"]["pass"], 2)
        self.assertEqual(report["counts"]["top_level"]["fail"], 0)
        self.assertEqual(report["counts"]["packages"]["pass"], 1)

    def test_interleaved_packages_and_parallel_tests(self):
        events = [event("start", "a"), event("start", "b"),
                  event("run", "a", "TestSame"), event("pause", "a", "TestSame"),
                  event("run", "b", "TestSame"), event("pass", "b", "TestSame"), event("pass", "b"),
                  event("cont", "a", "TestSame"), event("pass", "a", "TestSame"), event("pass", "a")]
        report = summarize(stream(events), 0, ["a", "b"])
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["counts"]["top_level"]["pass"], 2)
        self.assertEqual({r["package"] for r in report["test_results"]}, {"a", "b"})

    def test_repeated_test_retains_failure_and_occurrences(self):
        events = [event("start")]
        for action in ("pass", "fail", "pass"):
            events.extend([event("run", test="TestRepeated"), event(action, test="TestRepeated")])
        events.append(event("fail"))
        report = summarize(stream(events), 1)
        self.assertEqual(report["status"], "failed")
        self.assertTrue(report["complete"])
        self.assertEqual([r["occurrence"] for r in report["test_results"]], [1, 2, 3])
        self.assertEqual(report["counts"]["top_level"]["pass"], 2)
        self.assertEqual(report["counts"]["top_level"]["fail"], 1)

    def test_repeated_package_runs_are_not_deduplicated(self):
        report = summarize(stream(passing() + passing()), 0)
        self.assertEqual(report["counts"]["packages"]["pass"], 2)
        self.assertEqual([r["package_run"] for r in report["test_results"]], [1, 2])

    def test_skips_are_reported_separately(self):
        skipped = [event("start"), event("run", test="TestSkip"), event("skip", test="TestSkip"), event("pass")]
        report = summarize(stream(skipped), 0)
        self.assertEqual(report["status"], "skipped")
        self.assertEqual(report["counts"]["top_level"]["skip"], 1)
        self.assertEqual(summarize(stream(skipped + passing()), 0)["status"], "passed_with_skips")

    def test_no_test_packages_and_empty_selection_are_not_test_passes(self):
        for terminal in ("skip", "pass"):
            with self.subTest(terminal=terminal):
                report = summarize(stream([event("start"), event(terminal)]), 0)
                self.assertEqual(report["status"], "no_tests")
                self.assertEqual(report["counts"]["top_level"]["pass"], 0)

    def test_package_failure_without_failed_test(self):
        for details in ({}, {"FailedBuild": "dependency"}):
            report = summarize(stream([event("start"), event("fail", **details)]), 1)
            self.assertEqual(report["status"], "failed")
            self.assertEqual(report["counts"]["top_level"]["fail"], 0)
            self.assertEqual(report["counts"]["packages"]["fail"], 1)
        self.assertEqual(report["build_failures"], ["dependency"])

    def test_build_events_do_not_count_as_tests(self):
        events = [{"Action": "build-output", "ImportPath": "dep", "Output": "diagnostic"},
                  {"Action": "build-fail", "ImportPath": "dep"}]
        report = summarize(stream(events), 1)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["complete"])
        self.assertEqual(report["build_failures"], ["dep"])

    def test_unknown_exit_code_and_process_failure_cannot_pass(self):
        self.assertEqual(summarize(stream(passing()), None)["status"], "incomplete")
        self.assertEqual(summarize(stream(passing()), 1)["status"], "failed")
        self.assertEqual(summarize(stream(passing()), -9)["status"], "failed")
        with self.assertRaises(ValueError):
            summarize(stream(passing()), True)

    def test_incomplete_and_malformed_streams_cannot_pass(self):
        samples = ["", stream(passing())[:-1], stream(passing()[:-1]),
                   stream(passing()) + '{"Action":', stream(passing()) + 'plain stderr\n',
                   stream(passing()) + '[]\n', stream(passing()) + '{}\n',
                   stream(passing()) + '{"Action": "new-action", "Package": "p"}\n']
        for text in samples:
            with self.subTest(text=text):
                report = summarize(text, 0)
                self.assertFalse(report["complete"])
                self.assertNotEqual(report["status"], "passed")

    def test_timeout_preserves_unfinished_test_and_package_failure(self):
        events = [event("start"), event("run", test="TestHung"),
                  event("output", test="TestHung", Output="panic: test timed out\n"), event("fail")]
        report = summarize(stream(events), 1)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["complete"])
        self.assertEqual(report["unfinished_tests"][0]["test"], "TestHung")
        self.assertEqual(report["counts"]["top_level"]["fail"], 0)

    def test_duplicate_terminal_and_missing_run_are_incomplete(self):
        for events in (passing()[:-1] + [event("pass", test="TestOne"), event("pass")],
                       [event("start"), event("pass", test="TestOne"), event("pass")]):
            self.assertEqual(summarize(stream(events), 0)["status"], "incomplete")

    def test_expected_package_omission_is_detected(self):
        report = summarize(stream(passing("a")), 0, ["a", "b"])
        self.assertEqual(report["status"], "incomplete")
        self.assertIn("expected package absent: b", report["issues"])

    def test_examples_and_fuzz_seeds_are_not_unit_test_counts(self):
        report = summarize(stream(passing(name="ExampleOne") + passing(name="FuzzOne/seed#0")), 0)
        self.assertEqual(report["counts"]["top_level"]["pass"], 0)
        self.assertEqual(report["counts"]["examples"]["pass"], 1)
        self.assertEqual(report["counts"]["fuzz"]["pass"], 1)

    def test_package_pass_cannot_override_failed_test(self):
        events = [event("start"), event("run", test="TestBad"), event("fail", test="TestBad"), event("pass")]
        report = summarize(stream(events), 0)
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["complete"])

    def test_benchmarks_are_not_counted_as_passed_unit_tests(self):
        events = [event("start"), event("output", test="BenchmarkOne", Output="measurement"),
                  event("bench", test="BenchmarkOne"), event("pass")]
        report = summarize(stream(events), 0)
        self.assertTrue(report["complete"])
        self.assertEqual(report["status"], "no_tests")
        self.assertEqual(report["counts"]["benchmarks"]["bench"], 1)
        self.assertEqual(report["counts"]["top_level"]["pass"], 0)

    def test_cli_returns_test_status_and_log_identity(self):
        script = Path(__file__).resolve().parents[1] / "scripts/go_test_summary.py"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "go.jsonl"
            for code, events, expected_status in (
                (0, passing(), 0), (1, passing(), 1),
                (0, [event("start"), event("skip")], 2), (0, passing()[:-1], 2),
            ):
                path.write_text(stream(events), encoding="utf-8")
                result = subprocess.run([sys.executable, "-B", str(script), str(path), "--exit-code", str(code)],
                                        text=True, capture_output=True, check=False, timeout=10)
                self.assertEqual(result.returncode, expected_status, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report["exit_code"], code)
                self.assertEqual(report["source"]["path"], str(path.resolve()))
                self.assertEqual(len(report["source"]["sha256"]), 64)
