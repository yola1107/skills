"""Real Go event shapes and byte-preserving capture regressions."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_skills as checks
from scripts.go_test_summary import summarize, summarize_bytes
from test_go_test_summary import event, passing, stream


class SummaryBoundaryTests(unittest.TestCase):
    def test_benchmark_events_are_observations_not_completions(self):
        events = passing()[:-1] + [
            event("run", test="BenchmarkParent"),
            event("run", test="BenchmarkParent/child"),
            event("output", test="BenchmarkParent/child", Output="measurement"),
            event("run", test="BenchmarkParent/child"),
            event("bench", test="BenchmarkLogged"),
            event("bench", test="BenchmarkLogged"), event("pass"),
        ]
        report = summarize(stream(events), 0)
        self.assertEqual(report["status"], "passed")
        self.assertTrue(report["complete"])
        self.assertEqual(report["unfinished_tests"], [])
        self.assertEqual(report["counts"]["top_level"]["pass"], 1)
        self.assertEqual(report["counts"]["benchmarks"], {"pass": 0, "fail": 0, "skip": 0, "bench": 2})
        self.assertEqual([r["action"] for r in report["benchmark_events"]],
                         ["run", "run", "run", "bench", "bench"])
        logged = [r for r in report["test_results"] if r["test"] == "BenchmarkLogged"]
        self.assertEqual([r["occurrence"] for r in logged], [1, 2])

    def test_benchmark_exception_does_not_hide_incomplete_tests_or_packages(self):
        samples = [
            ([event("start"), event("run", test="BenchmarkOne")], 0),
            (passing()[:-1] + [event("run", test="BenchmarkOne"), event("pass")], None),
            ([event("start"), event("run", test="TestUnfinished"),
              event("run", test="BenchmarkOne"), event("pass")], 0),
        ]
        for events, code in samples:
            with self.subTest(events=events, exit_code=code):
                report = summarize(stream(events), code)
                self.assertEqual(report["status"], "incomplete")
                self.assertFalse(report["complete"])
        report = summarize(stream(samples[-1][0]), 0)
        self.assertEqual([r["test"] for r in report["unfinished_tests"]], ["TestUnfinished"])

    def test_benchmark_failures_and_skips_remain_explicit(self):
        for action, code, status in [("fail", 1, "failed"), ("skip", 0, "passed_with_skips")]:
            with self.subTest(action=action):
                events = passing()[:-1] + [event(action, test="BenchmarkOne"),
                                           event("fail" if action == "fail" else "pass")]
                report = summarize(stream(events), code)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["counts"]["benchmarks"][action], 1)
                self.assertTrue(report["complete"])
        events = passing()[:-1] + [event("fail", test="BenchmarkOne"), event("pass")]
        self.assertEqual(summarize(stream(events), 0)["status"], "failed")
        # A package-level failure still fails even without any benchmark result.
        events = passing()[:-1] + [event("run", test="BenchmarkOne"), event("fail")]
        self.assertEqual(summarize(stream(events), 1)["status"], "failed")

    def test_benchmarks_still_require_a_valid_package_run(self):
        for events in ([event("run", test="BenchmarkOne"), event("pass")],
                       passing() + [event("bench", test="BenchmarkOne")],
                       [event("start"), event("run", test="BenchmarkOne"),
                        event("pause", test="BenchmarkOne"), event("pass")]):
            with self.subTest(events=events):
                self.assertEqual(summarize(stream(events), 0)["status"], "incomplete")
        events = passing()[:-1] + [event("bench", test="TestOne"), event("pass")]
        self.assertEqual(summarize(stream(events), 0)["status"], "incomplete")

    def test_jsonl_uses_lf_not_unicode_line_boundaries(self):
        for separator in ("\u0085", "\u2028", "\u2029"):
            with self.subTest(separator=repr(separator)):
                events = passing()[:-1] + [event("output", Output="before" + separator + "after"), event("pass")]
                text = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in events)
                self.assertEqual(summarize(text, 0)["status"], "passed")
                self.assertEqual(summarize(text.replace("\n", "\r\n"), 0)["status"], "passed")
                # A Unicode separator outside JSON is not an ignorable blank record.
                self.assertEqual(summarize(stream(passing()) + separator + "\n", 0)["status"], "incomplete")
        self.assertEqual(summarize(stream(passing()) + '{"Action":\n', 0)["status"], "incomplete")

    def test_invalid_utf8_view_cannot_be_reported_as_complete(self):
        raw = stream(passing()[:-1]).encode() + b'{"Action":"output","Package":"example/p","Output":"\xff"}\n' + stream([event("pass")]).encode()
        for code, status in [(0, "incomplete"), (None, "incomplete"), (1, "failed")]:
            with self.subTest(exit_code=code):
                report = summarize_bytes(raw, code)
                self.assertEqual(report["status"], status)
                self.assertFalse(report["complete"])
                self.assertTrue(report["stdout_decode_error"])
                self.assertEqual(report["counts"]["top_level"]["pass"], 1)
        self.assertFalse(summarize_bytes(stream(passing()).encode(), 0)["stdout_decode_error"])

    def test_cli_unknown_exit_and_invalid_bytes_keep_log_identity(self):
        script = checks.ROOT / "scripts/go_test_summary.py"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stdout.jsonl"
            cases = [
                (stream(passing()).encode(), "unknown", "incomplete", 2),
                (stream(passing()).encode() + b'\xe6\xbc', "unknown", "incomplete", 2),
                (stream(passing()).encode() + b'\xff', "1", "failed", 1),
                (stream(passing()).encode(), "-9", "failed", 1),
            ]
            for raw, code, status, cli_code in cases:
                with self.subTest(exit_code=code, raw=raw):
                    path.write_bytes(raw)
                    result = subprocess.run([sys.executable, "-B", str(script), str(path), "--exit-code", code],
                                            capture_output=True, check=False, timeout=10)
                    report = json.loads(result.stdout)
                    self.assertEqual(result.returncode, cli_code, result.stderr)
                    self.assertEqual(report["status"], status)
                    self.assertEqual(report["exit_code"], None if code == "unknown" else int(code))
                    self.assertEqual(report["source"]["sha256"], hashlib.sha256(raw).hexdigest())
                    self.assertEqual(path.read_bytes(), raw)
            result = subprocess.run([sys.executable, "-B", str(script), str(path), "--exit-code", "invalid"],
                                    capture_output=True, check=False, timeout=10)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, b"")


class CaptureByteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="skills-capture-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.harness = checks.GoFixtureTests("runTest")
        self.harness.env = os.environ.copy()

    def assert_capture(self, directory, stdout, stderr):
        capture, = directory.iterdir()
        self.assertEqual((capture / "stdout.jsonl").read_bytes(), stdout)
        self.assertEqual((capture / "stderr.txt").read_bytes(), stderr)
        report = json.loads((capture / "summary.json").read_bytes())
        metadata = json.loads((capture / "capture.json").read_bytes())
        self.assertEqual(metadata["source"], report["source"])
        self.assertEqual(metadata["exit_code"], report["exit_code"])
        self.assertEqual(metadata["supervisor_timeout"], report["supervisor_timeout"])
        self.assertEqual(report["source"]["stdout_sha256"], hashlib.sha256(stdout).hexdigest())
        self.assertEqual(report["source"]["stderr_sha256"], hashlib.sha256(stderr).hexdigest())
        return report

    def test_normal_process_preserves_newlines_and_invalid_bytes(self):
        real_run = subprocess.run
        valid = stream(passing()).replace("\n", "\r\n").encode()
        cases = [
            (valid, b"line1\r\nline2\r\n", "passed", False),
            (valid, b"diagnostic\r\npartial \xe6\xbc\xff\r", "passed", True),
            (valid + b"\xff", b"stderr", "incomplete", False),
        ]
        for index, (stdout, stderr, status, stderr_error) in enumerate(cases):
            with self.subTest(index=index):
                evidence = self.root / str(index)
                def child(command, **kwargs):
                    self.assertIs(kwargs["text"], False)
                    code = f"import os; os.write(1, {stdout!r}); os.write(2, {stderr!r})"
                    return real_run([sys.executable, "-c", code], **kwargs)
                with patch.dict(os.environ, {"SKILLS_TEST_EVIDENCE": str(evidence)}):
                    with patch("test_skills.subprocess.run", side_effect=child):
                        report, _ = self.harness.go_test(["./..."], self.root)
                saved = self.assert_capture(evidence, stdout, stderr)
                self.assertEqual(report, saved)
                self.assertEqual(report["status"], status)
                self.assertEqual(report["stderr_decode_error"], stderr_error)
                self.assertFalse(report["supervisor_timeout"])
                self.assertEqual(report["exit_code"], 0)

    def test_timeout_preserves_partial_bytes_and_unknown_status(self):
        cases = [(b"partial ASCII", b"interrupted"),
                 (b'{"Action":"output","Output":"\xe6\xbc', b"\xff\r\n\xe6\xbc"),
                 (None, None)]
        for index, (stdout, stderr) in enumerate(cases):
            with self.subTest(index=index):
                evidence = self.root / str(index)
                exc = subprocess.TimeoutExpired(["go", "test"], 90, output=stdout, stderr=stderr)
                with patch.dict(os.environ, {"SKILLS_TEST_EVIDENCE": str(evidence)}):
                    with patch("test_skills.subprocess.run", side_effect=exc):
                        with self.assertRaises(subprocess.TimeoutExpired) as caught:
                            self.harness.go_test(["./..."], self.root)
                self.assertIs(caught.exception, exc)
                report = self.assert_capture(evidence, stdout or b"", stderr or b"")
                self.assertIsNone(report["exit_code"])
                self.assertEqual(report["status"], "incomplete")
                self.assertTrue(report["supervisor_timeout"])

    def test_raw_capture_precedes_summary_and_rejects_source_directory(self):
        evidence = self.root / "parse-failure"
        stdout, stderr = b"raw\r\n\xe6\xbc", b"err\xff"
        result = subprocess.CompletedProcess(["go", "test"], 0, stdout, stderr)
        with patch.dict(os.environ, {"SKILLS_TEST_EVIDENCE": str(evidence)}):
            with patch("test_skills.subprocess.run", return_value=result):
                with patch("test_skills.summarize_bytes", side_effect=ValueError("parser failure")):
                    with self.assertRaisesRegex(ValueError, "parser failure"):
                        self.harness.go_test(["./..."], self.root)
        capture, = evidence.iterdir()
        self.assertEqual((capture / "stdout.jsonl").read_bytes(), stdout)
        self.assertEqual((capture / "stderr.txt").read_bytes(), stderr)
        metadata = json.loads((capture / "capture.json").read_bytes())
        self.assertEqual(metadata["exit_code"], 0)
        self.assertEqual(metadata["source"]["stdout_sha256"], hashlib.sha256(stdout).hexdigest())
        self.assertEqual(metadata["source"]["stderr_sha256"], hashlib.sha256(stderr).hexdigest())
        with patch.dict(os.environ, {"SKILLS_TEST_EVIDENCE": str(checks.ROOT)}):
            with patch("test_skills.subprocess.run") as run:
                with self.assertRaises(ValueError):
                    self.harness.go_test(["./..."], self.root)
                run.assert_not_called()


@unittest.skipUnless(shutil.which("go"), "Go unavailable: real reporting regressions NOT executed")
class GoReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="skills-reporting-")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        cls.harness = checks.GoFixtureTests("runTest")
        cls.harness.root = cls.root
        # Only self-contained fixtures use these isolated settings.
        cls.harness.env = {k: v for k, v in os.environ.items() if not k.startswith(("GO", "CGO_"))}
        cls.harness.env.update({
            "GOENV": "off", "GOWORK": "off", "GOTOOLCHAIN": "local", "GOFLAGS": "",
            "GOPROXY": "off", "GOSUMDB": "off", "GOCACHE": str(cls.root / "cache"),
            "GOMODCACHE": str(cls.root / "modcache"),
        })
        cls.target = cls.harness.reporting_fixture("benchmarks", {"bench_test.go": r'''package sample

import "testing"

var sink int

func TestOne(t *testing.T) {}

func TestUnicode(t *testing.T) {
	t.Log("before\u0085middle\u2028next\u2029after")
}

func BenchmarkPlain(b *testing.B) {
	for i := 0; i < b.N; i++ {
		sink = i
	}
}

func BenchmarkLogged(b *testing.B) {
	b.Log("benchmark log")
	BenchmarkPlain(b)
}

func BenchmarkNested(b *testing.B) {
	b.Run("quiet", BenchmarkPlain)
	b.Run("logged", BenchmarkLogged)
}

func BenchmarkFail(b *testing.B) { b.Error("intentional benchmark failure") }
func BenchmarkSkip(b *testing.B) { b.Skip("intentional benchmark skip") }

func BenchmarkNestedFail(b *testing.B) {
	b.Run("bad", BenchmarkFail)
}
'''})

    def capture(self, args):
        # Inspect the actual captured JSON independently of the summary.
        directory = Path(os.environ.get("SKILLS_TEST_EVIDENCE", str(self.root / "captures"))) / "reporting-regressions"
        before = set(directory.iterdir()) if directory.exists() else set()
        with patch.dict(os.environ, {"SKILLS_TEST_EVIDENCE": str(directory)}):
            report, output = self.harness.go_test(args, self.target)
        capture, = set(directory.iterdir()) - before
        raw = (capture / "stdout.jsonl").read_bytes()
        events = [json.loads(line) for line in raw.split(b"\n") if line]
        script = checks.ROOT / "scripts/go_test_summary.py"
        cli = subprocess.run([sys.executable, "-B", str(script), str(capture / "stdout.jsonl"),
                              "--exit-code", str(report["exit_code"])], capture_output=True, check=False, timeout=10)
        self.assertEqual(json.loads(cli.stdout)["counts"], report["counts"])
        self.assertEqual(json.loads(cli.stdout)["status"], report["status"])
        return report, output, events, cli.returncode

    def test_real_successful_benchmark_shapes(self):
        cases = [("Plain", 1, "1"), ("Logged", 1, "1"), ("Nested", 1, "1"),
                 ("Plain", 3, "1"), ("Logged", 2, "1"), ("Nested", 2, "1,2")]
        for name, count, cpus in cases:
            with self.subTest(benchmark=name, count=count, cpus=cpus):
                report, output, events, cli_code = self.capture([
                    "-run=^TestOne$", "-bench=^Benchmark" + name + "$", "-benchtime=1x",
                    "-count=" + str(count), "-cpu=" + cpus, "-timeout=10s", "./...",
                ])
                self.assertEqual(report["exit_code"], 0, output)
                self.assertEqual(report["status"], "passed", (report, output))
                self.assertEqual(cli_code, 0)
                self.assertTrue(report["complete"])
                self.assertEqual(report["unfinished_tests"], [])
                self.assertEqual(report["counts"]["top_level"]["pass"], count * len(cpus.split(",")))
                observed = [(e["Test"], e["Action"]) for e in events
                            if e.get("Test", "").startswith("Benchmark") and e["Action"] != "output"]
                self.assertEqual([(e["test"], e["action"]) for e in report["benchmark_events"]], observed)
                results = [(e["Test"], e["Action"]) for e in events
                           if e.get("Test", "").startswith("Benchmark") and e["Action"] in {"pass", "fail", "skip", "bench"}]
                self.assertEqual([(e["test"], e["action"]) for e in report["test_results"]
                                  if e["kind"] == "benchmarks"], results)
                measurements = "".join(e.get("Output", "") for e in events)
                self.assertRegex(measurements, r"(?m)^Benchmark" + name + r"(?:/[^\s]+)?(?:-\d+)?\s+\d+\s+")

    def test_real_benchmark_only_is_complete_but_not_unit_validation(self):
        report, output, _, cli_code = self.capture([
            "-run=^$", "-bench=^BenchmarkPlain$", "-benchtime=1x", "-count=2", "-timeout=10s", "./...",
        ])
        self.assertEqual(report["exit_code"], 0, output)
        self.assertEqual(report["status"], "no_tests")
        self.assertTrue(report["complete"])
        self.assertEqual(report["counts"]["top_level"]["pass"], 0)
        self.assertEqual(cli_code, 2)

    def test_real_benchmark_failure_and_skip_are_not_hidden(self):
        for name, status, cli_code in [("Fail", "failed", 1), ("NestedFail", "failed", 1),
                                      ("Skip", "passed_with_skips", 2)]:
            with self.subTest(benchmark=name):
                report, output, _, actual_cli = self.capture([
                    "-run=^TestOne$", "-bench=^Benchmark" + name + "$", "-benchtime=1x",
                    "-count=1", "-timeout=10s", "./...",
                ])
                self.assertEqual(report["status"], status, (report, output))
                self.assertEqual(actual_cli, cli_code)
                action = "skip" if name == "Skip" else "fail"
                self.assertGreater(report["counts"]["benchmarks"][action], 0)
                self.assertEqual(report["counts"]["top_level"]["pass"], 1)
                self.assertEqual(report["exit_code"] == 0, name == "Skip")

    def test_real_unicode_output_is_valid_jsonl(self):
        report, output, events, cli_code = self.capture(["-run=^TestUnicode$", "-count=1", "-timeout=10s", "./..."])
        self.assertEqual(report["status"], "passed", (report, output))
        self.assertEqual(cli_code, 0)
        self.assertEqual(report["counts"]["top_level"]["pass"], 1)
        self.assertTrue(any("\u0085" in e.get("Output", "") for e in events))
