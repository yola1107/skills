"""Offline repository checks, not model/agent evaluations (Python 3.9+)."""

import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.go_test_summary import summarize_bytes

SKILLS = ("go-code-review", "go-code-simplifier")
CLEANUP_TESTS = {
    'TestLoadDiscardsPartialValue',
    'TestRunRecordsWorkError',
    'TestRunRecordsDuringPanic',
    'TestFirstIsOnePreservesShortCircuit',
    'TestEmptyIDsMarshalAsNull',
    'TestCopyBytesPreservesOwnershipAndNil',
    'TestCopyBytesPreservesExactCapacity',
    'TestNormalizeName',
    'TestRelayPreservesPartialValueAndEOF',
    'TestOneShotCompletes',
    'TestTypedNilContract',
    'TestCallSiteIdentity',
}
BOUNDARY_TESTS = {
    'TestFetchReportChecksStatusAndCloses',
    'TestFetchReportLimitsActualBytes',
    'TestFetchReportPreservesReadError',
    'TestReportClientRefusesRedirects',
    'TestScanLinesPreservesTerminalError',
    'TestCountRowsPreservesTerminalError',
    'TestWriteAuditDoesNotExposeToken',
    'TestTLSConfigVerifiesIdentity',
    'TestTLSConfigRejectsMissingTrust',
    'TestWordAtPreservesAliasAndBounds',
}

SAFE_DIFF = [
    "git", "--no-pager", "--no-optional-locks", "-c", "core.fsmonitor=false",
    "diff", "--no-ext-diff", "--no-textconv",
]


def run(args: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    """Never invoke a shell; callers check each expected exit status."""
    return subprocess.run(
        args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, timeout=90, check=False,
    )


def markdown_links(path: Path) -> list[str]:
    # Inline-link check for this repository, not a general Markdown parser.
    text = re.sub(r"^```.*?^```[^\n]*", "", path.read_text(encoding="utf-8"), flags=re.M | re.S)
    return re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text)


def heading_anchors(path: Path) -> set[str]:
    headings = re.findall(r"^#{1,6}\s+(.+)$", path.read_text(encoding="utf-8"), re.M)
    return {re.sub(r"[^\w\- ]", "", h.lower()).replace(" ", "-") for h in headings}


def apply_setup_edits(target: Path, edits: list[dict]) -> None:
    """Apply supervisor-owned evaluation setup, never model-supplied commands."""
    pending = {}
    root = target.resolve()
    for edit in edits:
        path = (root / edit["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("setup path must be an existing fixture file")
        if path.suffix != ".go" or path.name.endswith("_test.go"):
            raise ValueError("setup may only change fixture implementation files")
        before, after = edit["before"], edit["after"]
        text = pending.get(path, path.read_text(encoding="utf-8"))
        if not before or text.count(before) != 1 or before == after:
            raise ValueError("setup replacement must have exactly one target and a change")
        pending[path] = text.replace(before, after)
    # Validate every edit before writing anything.
    for path, text in pending.items():
        path.write_text(text, encoding="utf-8")


class DocumentTests(unittest.TestCase):
    def test_required_entry_fields(self):
        # Basic required fields, not a general YAML validator.
        for skill in SKILLS:
            with self.subTest(skill=skill):
                text = (ROOT / skill / "SKILL.md").read_text(encoding="utf-8")
                match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
                self.assertIsNotNone(match, "missing frontmatter")
                fields = {}
                for key in ("name", "description"):
                    values = re.findall(rf"^{key}: (.+)$", match.group(1), re.M)
                    self.assertEqual(len(values), 1, f"expected one {key}")
                    fields[key] = values[0]
                self.assertEqual(fields["name"], skill)
                self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertLessEqual(len(fields["name"]), 64)
                self.assertTrue(1 <= len(fields["description"]) <= 1024)

    def test_local_document_links(self):
        docs = [ROOT / "README.md", ROOT / "THIRD_PARTY_NOTICES.md", ROOT / "evals/README.md"]
        for skill in SKILLS:
            docs.extend((ROOT / skill).rglob("*.md"))
        for doc in docs:
            for link in markdown_links(doc):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc:
                    continue  # Offline checks do not fetch external links.
                with self.subTest(document=str(doc.relative_to(ROOT)), link=link):
                    target = (doc.parent / unquote(parsed.path)).resolve() if parsed.path else doc
                    self.assertTrue(target.is_relative_to(ROOT), "link escapes repository")
                    self.assertTrue(target.is_file(), "missing linked file")
                    if parsed.fragment:
                        self.assertIn(unquote(parsed.fragment), heading_anchors(target))

    def test_single_skill_install_retains_notice_and_references(self):
        for skill in SKILLS:
            with self.subTest(skill=skill), tempfile.TemporaryDirectory() as tmp:
                install = Path(tmp) / ".agents/skills"
                install.mkdir(parents=True)
                shutil.copytree(ROOT / skill, install / skill)
                shutil.copy2(ROOT / "THIRD_PARTY_NOTICES.md", install / "THIRD_PARTY_NOTICES.md")
                self.assertTrue((install / skill / "SKILL.md").is_file())
                self.assertEqual((install / "THIRD_PARTY_NOTICES.md").read_bytes(), (ROOT / "THIRD_PARTY_NOTICES.md").read_bytes())
                for doc in (install / skill).rglob("*.md"):
                    for link in markdown_links(doc):
                        parsed = urlsplit(link)
                        if not parsed.scheme and not parsed.netloc and parsed.path:
                            self.assertTrue((doc.parent / unquote(parsed.path)).is_file(), link)

    def test_documented_git_command_matches_tested_command(self):
        text = (ROOT / "go-code-review/references/read-only-validation.md").read_text(encoding="utf-8")
        commands = re.findall(r"^git .+$", text, re.M)
        self.assertEqual(len(commands), 1)
        self.assertEqual(shlex.split(commands[0]), SAFE_DIFF)

    def test_license_texts_are_preserved(self):
        text = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```text\n(.*?)```", text, re.S)
        self.assertEqual(
            [hashlib.sha256(block.encode()).hexdigest() for block in blocks],
            ["30b4dc1b33c299fadf455500c5431d4b7e036dd8685b3398dfc99808f4e3ed32",
             "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"],
            "license bodies differ from the fixed upstream baseline",
        )

    def test_evaluation_answers_are_not_loaded_by_skill_links(self):
        for skill in SKILLS:
            for doc in (ROOT / skill).rglob("*.md"):
                for link in markdown_links(doc):
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    target = (doc.parent / unquote(parsed.path)).resolve()
                    self.assertFalse(target.is_relative_to(ROOT / "evals"), link)
                    self.assertFalse(target.is_relative_to(ROOT / "tests"), link)

    def test_setup_edits_reject_unsafe_or_ambiguous_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            shutil.copytree(ROOT / "evals/fixtures/access", target / "fixture")
            fixture = target / "fixture"
            snapshot = {p: p.read_bytes() for p in fixture.iterdir()}
            bad_edits = [
                {"path": "../outside.go", "before": "a", "after": "b"},
                {"path": "access_test.go", "before": "package access", "after": "package changed"},
                {"path": "access.go", "before": "absent target", "after": "replacement"},
            ]
            for edit in bad_edits:
                with self.subTest(edit=edit), self.assertRaises(ValueError):
                    apply_setup_edits(fixture, [edit])
            valid = {"path": "access.go", "before": "authenticated || ownerID", "after": "authenticated && ownerID"}
            with self.assertRaises(ValueError):
                apply_setup_edits(fixture, [valid, bad_edits[-1]])
            for path, data in snapshot.items():
                self.assertEqual(path.read_bytes(), data)

    def test_evaluation_manifest_has_real_inputs(self):
        manifest = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema_version"], 1)
        seen = set()
        for case in manifest["cases"]:
            with self.subTest(case=case["id"]):
                self.assertNotIn(case["id"], seen)
                seen.add(case["id"])
                fixture = (ROOT / case["fixture"]).resolve()
                self.assertTrue(fixture.is_relative_to(ROOT / "evals/fixtures"))
                self.assertTrue((fixture / "go.mod").is_file())
                self.assertTrue(list(fixture.glob("*_test.go")))
                self.assertTrue(case["prompt"] and case["expected_output"] and case["assertions"])
                self.assertTrue(set(case["skills"]).issubset(SKILLS))
                if case.get("setup_edits"):
                    self.assertEqual(len({e["id"] for e in case["setup_edits"]}), len(case["setup_edits"]))
                    with tempfile.TemporaryDirectory() as tmp:
                        target = Path(tmp) / "fixture"
                        shutil.copytree(fixture, target)
                        apply_setup_edits(target, case["setup_edits"])
                        for original in fixture.glob("*_test.go"):
                            self.assertEqual(original.read_bytes(), (target / original.name).read_bytes())


@unittest.skipUnless(shutil.which("git"), "Git unavailable: query regressions NOT executed")
class GitQueryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="skills-git-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update({
            "HOME": str(self.root), "XDG_CONFIG_HOME": str(self.root / "xdg"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_ATTR_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
        })
        self.git("init", "--quiet")
        (self.repo / "sample.txt").write_text("old\n", encoding="utf-8")
        self.git("add", "sample.txt")
        (self.repo / "sample.txt").write_text("new content\n", encoding="utf-8")
        self.marker = self.root / "executed"
        self.helper = self.root / "probe.py"
        self.helper.write_text(
            "from pathlib import Path\nimport sys\n"
            "mode, marker = sys.argv[1:3]\n"
            "Path(marker).write_text('executed', encoding='utf-8')\n"
            "if mode == 'textconv':\n"
            "    sys.stdout.buffer.write(Path(sys.argv[-1]).read_bytes())\n"
            "elif mode == 'clean':\n"
            "    sys.stdout.buffer.write(sys.stdin.buffer.read())\n",
            encoding="utf-8",
        )

    def git(self, *args):
        result = run(["git", *args], self.repo, self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        return result

    def helper_command(self, mode):
        return shlex.join([sys.executable, str(self.helper), mode, str(self.marker)])

    def protected_diff(self):
        result = run(SAFE_DIFF, self.repo, self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        return result

    def test_no_optional_locks_still_runs_textconv(self):
        (self.repo / ".gitattributes").write_text("*.txt diff=probe\n", encoding="utf-8")
        self.git("config", "diff.probe.textconv", self.helper_command("textconv"))
        self.git("--no-pager", "--no-optional-locks", "diff")
        self.assertTrue(self.marker.exists(), "textconv reproduction did not execute")

    def test_protected_diff_blocks_textconv_and_keeps_index(self):
        (self.repo / ".gitattributes").write_text("*.txt diff=probe\n", encoding="utf-8")
        self.git("config", "diff.probe.textconv", self.helper_command("textconv"))
        before = {name: (self.repo / name).read_bytes() for name in (".git/index", ".git/HEAD", "sample.txt")}
        result = self.protected_diff()
        self.assertIn("new content", result.stdout)
        self.assertFalse(self.marker.exists())
        for name, content in before.items():
            self.assertEqual((self.repo / name).read_bytes(), content, name)

    def test_protected_diff_blocks_external_diff(self):
        self.git("config", "diff.external", self.helper_command("external"))
        self.git("--no-pager", "--no-optional-locks", "diff")
        self.assertTrue(self.marker.exists(), "external diff reproduction did not execute")
        self.marker.unlink()
        result = self.protected_diff()
        self.assertIn("new content", result.stdout)
        self.assertFalse(self.marker.exists())

    def test_protected_diff_is_not_a_clean_filter_sandbox(self):
        (self.repo / ".gitattributes").write_text("*.txt filter=probe\n", encoding="utf-8")
        self.git("config", "filter.probe.clean", self.helper_command("clean"))
        self.protected_diff()
        self.assertTrue(self.marker.exists(), "clean-filter caveat no longer reproduced; investigate")


@unittest.skipUnless(shutil.which("go") and shutil.which("gofmt"), "Go/gofmt unavailable: Go validation NOT executed")
class GoFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="skills-go-")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name)
        # These overrides apply only to self-contained fixtures, not user projects.
        cls.env = {k: v for k, v in os.environ.items() if not k.startswith(("GO", "CGO_"))}
        cls.env.update({
            "GOENV": "off", "GOWORK": "off", "GOTOOLCHAIN": "local",
            "GOFLAGS": "", "GOPROXY": "off", "GOSUMDB": "off",
            "GOCACHE": str(cls.root / "cache"), "GOMODCACHE": str(cls.root / "modcache"),
        })
        cls.fixtures = cls.root / "fixtures"
        shutil.copytree(ROOT / "evals/fixtures", cls.fixtures)

    def assert_success(self, args, cwd):
        result = run(args, cwd, self.env)
        self.assertEqual(result.returncode, 0, result.stdout)
        return result

    def go_test(self, args, cwd):
        command = ["go", "test", "-json", *args]
        evidence = os.environ.get("SKILLS_TEST_EVIDENCE")
        capture = None
        if evidence:
            directory = Path(evidence).resolve()
            if directory.is_relative_to(ROOT):
                raise ValueError("test evidence must be outside the source repository")
            directory.mkdir(parents=True, exist_ok=True)
            capture = Path(tempfile.mkdtemp(prefix="go-test-", dir=directory))
        # Binary capture avoids newline conversion and decoding before preservation.
        timeout_error = None
        try:
            result = subprocess.run(command, cwd=cwd, env=self.env, text=False,
                                    capture_output=True, timeout=90, check=False)
        except subprocess.TimeoutExpired as exc:
            timeout_error = exc
            # No observed Go exit status; preserve the partial bytes exactly.
            result = subprocess.CompletedProcess(command, None, exc.stdout or b"", exc.stderr or b"")
        raw_stdout, raw_stderr = result.stdout, result.stderr
        if capture:
            (capture / "stdout.jsonl").write_bytes(raw_stdout)
            (capture / "stderr.txt").write_bytes(raw_stderr)
            source = {
                "command": command, "cwd": str(cwd),
                "stdout_sha256": hashlib.sha256(raw_stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(raw_stderr).hexdigest(),
            }
            metadata = {"source": source, "exit_code": result.returncode,
                        "supervisor_timeout": timeout_error is not None}
            (capture / "capture.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        report = summarize_bytes(raw_stdout, result.returncode)
        report["supervisor_timeout"] = timeout_error is not None
        stdout = raw_stdout.decode("utf-8", errors="replace")
        try:
            stderr = raw_stderr.decode("utf-8")
            report["stderr_decode_error"] = False
        except UnicodeDecodeError:
            stderr = raw_stderr.decode("utf-8", errors="replace")
            report["stderr_decode_error"] = True
        if capture:
            report["source"] = source
            (capture / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if timeout_error is not None:
            raise timeout_error
        return report, stdout + stderr

    def assert_go_pass(self, args, cwd, names=None):
        report, output = self.go_test(args, cwd)
        self.assertEqual(report["status"], "passed", (report, output))
        self.assertTrue(report["complete"], (report, output))
        if names is not None:
            self.assertEqual(
                sorted((x["test"], x["action"]) for x in report["test_results"] if x["kind"] == "top_level"),
                sorted((name, "pass") for name in names),
                "unexpected top-level contract results",
            )
        return report

    def assert_contract_failure(self, report, test, output):
        self.assertNotEqual(report["exit_code"], 0, output)
        self.assertEqual(report["status"], "failed", (report, output))
        self.assertTrue(report["complete"], (report, output))
        self.assertIn(test, [x["test"] for x in report["test_results"] if x["action"] == "fail"],
                      "expected named assertion failure, not just a package/build failure")

    def reporting_fixture(self, name, files):
        target = self.root / name
        target.mkdir()
        (target / "go.mod").write_text("module example.com/reporting\n\ngo 1.22\n", encoding="utf-8")
        for path, text in files.items():
            source = target / path
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text(text, encoding="utf-8")
        return target

    def test_reporter_real_repeats_subtests_and_packages(self):
        source = '''package sample
import "testing"
func TestSame(t *testing.T) {
    t.Log("--- PASS: TestForged")
    t.Run("child", func(t *testing.T) { t.Parallel() })
}
'''
        target = self.reporting_fixture("report-repeats", {
            "a/same_test.go": source + 'func TestSkip(t *testing.T) { t.Skip("intentional") }\n',
            "b/same_test.go": source,
            "empty/empty.go": "package empty\n",
        })
        report, output = self.go_test(["-count=2", "-timeout=30s", "./..."], target)
        self.assertTrue(report["complete"], (report, output))
        self.assertEqual(report["status"], "passed_with_skips")
        self.assertEqual(report["counts"]["top_level"]["pass"], 4)
        self.assertEqual(report["counts"]["top_level"]["skip"], 2)
        self.assertEqual(report["counts"]["subtests"]["pass"], 4)
        self.assertEqual(report["counts"]["packages"], {"pass": 2, "fail": 0, "skip": 1})
        same = [r for r in report["test_results"] if r["test"] == "TestSame"]
        self.assertEqual({(r["package"], r["occurrence"]) for r in same},
                         {(f"example.com/reporting/{p}", n) for p in ("a", "b") for n in (1, 2)})

    def test_reporter_real_build_failure(self):
        target = self.reporting_fixture("report-build", {"bad.go": "package bad\nvar X = undefinedName\n"})
        report, output = self.go_test(["-count=1", "./..."], target)
        self.assertEqual(report["status"], "failed", (report, output))
        self.assertNotEqual(report["exit_code"], 0)
        self.assertEqual(report["counts"]["top_level"]["fail"], 0)
        self.assertIn("undefined", output)

    def test_reporter_real_testmain_failure_before_and_after_tests(self):
        for when in ("before", "after"):
            with self.subTest(when=when):
                run = "m.Run();" if when == "after" else ""
                source = ('package sample\nimport ("os"; "testing")\n'
                          + 'func TestOne(t *testing.T) {}\n'
                          + f"func TestMain(m *testing.M) {{ {run} os.Exit(2) }}\n")
                target = self.reporting_fixture("report-main-" + when, {"main_test.go": source})
                report, output = self.go_test(["-count=1", "./..."], target)
                self.assertEqual(report["status"], "failed", (report, output))
                self.assertEqual(report["counts"]["packages"]["fail"], 1)
                self.assertEqual(report["counts"]["top_level"]["fail"], 0)
                self.assertEqual(report["counts"]["top_level"]["pass"], int(when == "after"))

    def test_reporter_real_timeout(self):
        target = self.reporting_fixture("report-timeout", {"wait_test.go":
            'package sample\nimport ("testing"; "time")\n'
            'func TestWait(t *testing.T) { for { time.Sleep(time.Second) } }\n'})
        report, output = self.go_test(["-count=1", "-timeout=100ms", "./..."], target)
        self.assertEqual(report["status"], "failed", (report, output))
        self.assertNotEqual(report["exit_code"], 0)
        self.assertIn("test timed out", output)
        self.assertEqual(report["counts"]["packages"]["fail"], 1)
        self.assertEqual(report["counts"]["top_level"]["pass"], 0)

    def test_reporter_supervisor_timeout_retains_partial_evidence(self):
        directory = self.root / "supervisor-timeout-evidence"
        partial = b'{"Action":"start","Package":"example.com/reporting"}\n'
        error = subprocess.TimeoutExpired(["go", "test"], 90, output=partial, stderr=b"interrupted")
        with patch.dict(os.environ, {"SKILLS_TEST_EVIDENCE": str(directory)}):
            with patch("test_skills.subprocess.run", side_effect=error):
                with self.assertRaises(subprocess.TimeoutExpired):
                    self.go_test(["./..."], self.fixtures / "cleanup")
        capture, = directory.iterdir()
        report = json.loads((capture / "summary.json").read_text())
        self.assertEqual(report["status"], "incomplete")
        self.assertIsNone(report["exit_code"])
        self.assertTrue(report["supervisor_timeout"])
        self.assertEqual((capture / "stdout.jsonl").read_bytes(), partial)
        self.assertEqual((capture / "stderr.txt").read_text(), "interrupted")

    def test_reporter_real_empty_selection_is_not_validation(self):
        report, output = self.go_test(["-count=1", "-run", "^NoSuchTest$", "./..."], self.fixtures / "cleanup")
        self.assertEqual(report["status"], "no_tests", (report, output))
        self.assertTrue(report["complete"])
        self.assertEqual(report["test_results"], [])

    def test_go_format(self):
        paths = [str(p) for p in sorted(self.fixtures.rglob("*.go"))]
        result = self.assert_success(["gofmt", "-l", *paths], self.fixtures)
        self.assertEqual(result.stdout, "", "fixture formatting differs from gofmt")

    def test_go_vet(self):
        for name in ("cleanup", "access", "boundaries"):
            with self.subTest(fixture=name):
                self.assert_success(["go", "vet", "./..."], self.fixtures / name)

    def test_cleanup_contracts_pass(self):
        self.assert_go_pass(["-count=1", "-timeout=30s", "./..."], self.fixtures / "cleanup", CLEANUP_TESTS)

    def test_access_defect_fails_and_minimal_fix_passes(self):
        target = self.root / "access-fixed"
        shutil.copytree(self.fixtures / "access", target)
        args = ["-count=1", "-timeout=30s", "./..."]
        report, output = self.go_test(args, target)
        self.assert_contract_failure(report, "TestCanAccessRequiresAuthenticationAndOwnership", output)
        source = target / "access.go"
        text = source.read_text(encoding="utf-8")
        self.assertEqual(text.count("authenticated || ownerID == callerID"), 1)
        source.write_text(text.replace("authenticated || ownerID == callerID", "authenticated && ownerID == callerID"), encoding="utf-8")
        self.assert_go_pass(args, target, {"TestCanAccessRequiresAuthenticationAndOwnership"})

    def test_non_equivalent_mutations_are_detected(self):
        mutations = [
            ("partial", "TestLoadDiscardsPartialValue", "return 0, err", "return value, err"),
            ("defer", "TestRunRecordsWorkError", "err = work()\n\treturn err", "return work()"),
            ("panic_defer", "TestRunRecordsDuringPanic",
             "var err error\n\tdefer func() { record(err) }()\n\terr = work()\n\treturn err",
             "err := work()\n\trecord(err)\n\treturn err"),
            ("capacity", "TestCopyBytesPreservesExactCapacity",
             "result := make([]byte, len(data))", "result := make([]byte, len(data), len(data)+1)"),
            ("short_circuit", "TestFirstIsOnePreservesShortCircuit",
             "return len(values) > 0 && values[0] == 1", "isOne := values[0] == 1\n\treturn len(values) > 0 && isOne"),
            ("nil_empty", "TestEmptyIDsMarshalAsNull", "var ids []int", "ids := []int{}"),
            ("alias", "TestCopyBytesPreservesOwnershipAndNil",
             "result := make([]byte, len(data))\n\tcopy(result, data)\n\treturn result", "return data"),
            ("caller", "TestCallSiteIdentity",
             "func CallSite() string {\n\treturn currentCaller()\n}",
             "func CallSite() string {\n\treturn extractedCaller()\n}\n\n//go:noinline\nfunc extractedCaller() string {\n\treturn currentCaller()\n}"),
        ]
        for name, test, before, after in mutations:
            with self.subTest(mutation=name):
                target = self.root / ("mutation-" + name)
                shutil.copytree(self.fixtures / "cleanup", target)
                source = target / "cleanup.go"
                text = source.read_text(encoding="utf-8")
                self.assertEqual(text.count(before), 1, "mutation target must be unique")
                source.write_text(text.replace(before, after), encoding="utf-8")
                self.assert_success(["go", "build", "./..."], target)
                if name in {"panic_defer", "capacity"}:
                    old_tests = CLEANUP_TESTS - {"TestRunRecordsDuringPanic", "TestCopyBytesPreservesExactCapacity"}
                    self.assert_go_pass(["-count=1", "-timeout=30s", "-run", "^(" + "|".join(sorted(old_tests)) + ")$", "./..."], target, old_tests)
                args = ["-count=1", "-timeout=30s", "-run", "^" + test + "$", "./..."]
                report, output = self.go_test(args, target)
                self.assert_contract_failure(report, test, output)
                source.write_text(text, encoding="utf-8")
                self.assert_go_pass(args, target, {test})

    def boundary_defect_case(self):
        cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))["cases"]
        return next(case for case in cases if case["id"] == "review-boundary-defects")

    def format_go(self, target):
        self.assert_success(["gofmt", "-w", *map(str, sorted(target.glob("*.go")))], target)

    def test_boundary_contracts_pass(self):
        self.assert_go_pass(["-count=1", "-timeout=30s", "./..."], self.fixtures / "boundaries", BOUNDARY_TESTS)

    def test_boundary_mutations_fail_and_repairs_pass(self):
        for edit in self.boundary_defect_case()["setup_edits"]:
            with self.subTest(mutation=edit["id"]):
                target = self.root / ("boundary-" + edit["id"])
                shutil.copytree(self.fixtures / "boundaries", target)
                source = target / edit["path"]
                original = source.read_bytes()
                apply_setup_edits(target, [edit])
                self.format_go(target)
                self.assert_success(["go", "build", "./..."], target)
                args = ["-count=1", "-timeout=30s", "-run", "^" + edit["expected_test"] + "$", "./..."]
                report, output = self.go_test(args, target)
                self.assert_contract_failure(report, edit["expected_test"], output)
                source.write_bytes(original)
                self.assert_go_pass(args, target, {edit["expected_test"]})

    def test_combined_boundary_defect_case_is_executable(self):
        target = self.root / "boundary-combined"
        shutil.copytree(self.fixtures / "boundaries", target)
        edits = self.boundary_defect_case()["setup_edits"]
        apply_setup_edits(target, edits)
        self.format_go(target)
        self.assert_success(["go", "build", "./..."], target)
        report, output = self.go_test(["-count=1", "-timeout=30s", "./..."], target)
        # Removing Body.Close also violates the read-error path's close assertion.
        expected = {edit["expected_test"] for edit in edits} | {"TestFetchReportPreservesReadError"}
        actual = {x["test"] for x in report["test_results"] if x["kind"] == "top_level" and x["action"] == "fail"}
        self.assertEqual(actual, expected, (report, output))
        for name in expected:
            self.assert_contract_failure(report, name, output)

    def test_boundary_checkptr(self):
        self.assert_go_pass(["-count=1", "-timeout=30s", "-gcflags=all=-d=checkptr=2", "./..."], self.fixtures / "boundaries", BOUNDARY_TESTS)

    def test_split_uintptr_is_diagnosed_not_executed(self):
        target = self.root / "uintptr-split"
        shutil.copytree(self.fixtures / "boundaries", target)
        source = target / "unsafe.go"
        original = source.read_bytes()
        apply_setup_edits(target, [{
            "path": "unsafe.go",
            "before": "return (*uint32)(unsafe.Pointer(uintptr(ptr) + uintptr(index)*unsafe.Sizeof(words[0])))",
            "after": "addr := uintptr(ptr)\n\treturn (*uint32)(unsafe.Pointer(addr + uintptr(index)*unsafe.Sizeof(words[0])))",
        }])
        self.format_go(target)
        self.assert_success(["go", "build", "./..."], target)
        result = run(["go", "vet", "./..."], target, self.env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("possible misuse of unsafe.Pointer", result.stdout)
        source.write_bytes(original)
        self.assert_success(["go", "vet", "./..."], target)

    def test_safe_index_rewrite_preserves_contracts(self):
        target = self.root / "safe-index"
        shutil.copytree(self.fixtures / "boundaries", target)
        apply_setup_edits(target, [
            {"path": "unsafe.go", "before": 'import "unsafe"\n', "after": ""},
            {"path": "unsafe.go",
             "before": "ptr := unsafe.Pointer(&words[0])\n\treturn (*uint32)(unsafe.Pointer(uintptr(ptr) + uintptr(index)*unsafe.Sizeof(words[0])))",
             "after": "return &words[index]"},
        ])
        self.format_go(target)
        self.assert_success(["go", "vet", "./..."], target)
        self.assert_go_pass(["-count=1", "-timeout=30s", "./..."], target, BOUNDARY_TESTS)

    @unittest.skipUnless(os.environ.get("SKILLS_RUN_RACE") == "1", "optional race check: set SKILLS_RUN_RACE=1")
    def test_boundaries_race(self):
        self.assert_go_pass(["-race", "-count=1", "-timeout=30s", "./..."], self.fixtures / "boundaries", BOUNDARY_TESTS)

    @unittest.skipUnless(os.environ.get("SKILLS_RUN_RACE") == "1", "optional race check: set SKILLS_RUN_RACE=1")
    def test_cleanup_race(self):
        self.assert_go_pass(["-race", "-count=1", "-timeout=30s", "./..."], self.fixtures / "cleanup", CLEANUP_TESTS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
