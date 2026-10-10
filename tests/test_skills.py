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
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("go-code-review", "go-code-simplifier")
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

    def test_go_format(self):
        paths = [str(p) for p in sorted(self.fixtures.rglob("*.go"))]
        result = self.assert_success(["gofmt", "-l", *paths], self.fixtures)
        self.assertEqual(result.stdout, "", "fixture formatting differs from gofmt")

    def test_go_vet(self):
        for name in ("cleanup", "access", "boundaries"):
            with self.subTest(fixture=name):
                self.assert_success(["go", "vet", "./..."], self.fixtures / name)

    def test_cleanup_contracts_pass(self):
        result = self.assert_success(["go", "test", "-count=1", "-timeout=30s", "-v", "./..."], self.fixtures / "cleanup")
        self.assertIn("--- PASS: TestCallSiteIdentity", result.stdout)
        self.assertEqual(result.stdout.count("--- PASS: Test"), 10, result.stdout)

    def test_access_defect_fails_and_minimal_fix_passes(self):
        target = self.root / "access-fixed"
        shutil.copytree(self.fixtures / "access", target)
        cmd = ["go", "test", "-count=1", "-timeout=30s", "./..."]
        before = run(cmd, target, self.env)
        self.assertNotEqual(before.returncode, 0, "intentional defect was not detected")
        self.assertIn("--- FAIL: TestCanAccessRequiresAuthenticationAndOwnership", before.stdout)
        source = target / "access.go"
        text = source.read_text(encoding="utf-8")
        self.assertEqual(text.count("authenticated || ownerID == callerID"), 1)
        source.write_text(text.replace("authenticated || ownerID == callerID", "authenticated && ownerID == callerID"), encoding="utf-8")
        self.assert_success(cmd, target)

    def test_non_equivalent_mutations_are_detected(self):
        mutations = [
            ("partial", "TestLoadDiscardsPartialValue", "return 0, err", "return value, err"),
            ("defer", "TestRunRecordsWorkError", "err = work()\n\treturn err", "return work()"),
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
                result = run(["go", "test", "-count=1", "-timeout=30s", "-run", "^" + test + "$", "./..."], target, self.env)
                self.assertNotEqual(result.returncode, 0, "non-equivalent mutation survived")
                self.assertIn("--- FAIL: " + test, result.stdout, "expected contract failure, not a build error")

    def boundary_defect_case(self):
        cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))["cases"]
        return next(case for case in cases if case["id"] == "review-boundary-defects")

    def format_go(self, target):
        self.assert_success(["gofmt", "-w", *map(str, sorted(target.glob("*.go")))], target)

    def test_boundary_contracts_pass(self):
        result = self.assert_success(["go", "test", "-count=1", "-timeout=30s", "-v", "./..."], self.fixtures / "boundaries")
        self.assertEqual(len(re.findall(r"^--- PASS: Test", result.stdout, re.M)), 10, result.stdout)
        self.assertNotIn("SKIP", result.stdout)

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
                cmd = ["go", "test", "-count=1", "-timeout=30s", "-run", "^" + edit["expected_test"] + "$", "./..."]
                result = run(cmd, target, self.env)
                self.assertNotEqual(result.returncode, 0, "seeded defect survived")
                self.assertIn("--- FAIL: " + edit["expected_test"], result.stdout, "expected assertion failure, not build failure")
                source.write_bytes(original)
                self.assert_success(cmd, target)

    def test_combined_boundary_defect_case_is_executable(self):
        target = self.root / "boundary-combined"
        shutil.copytree(self.fixtures / "boundaries", target)
        edits = self.boundary_defect_case()["setup_edits"]
        apply_setup_edits(target, edits)
        self.format_go(target)
        self.assert_success(["go", "build", "./..."], target)
        result = run(["go", "test", "-count=1", "-timeout=30s", "./..."], target, self.env)
        self.assertNotEqual(result.returncode, 0)
        for name in {edit["expected_test"] for edit in edits}:
            self.assertIn("--- FAIL: " + name, result.stdout)

    def test_boundary_checkptr(self):
        self.assert_success(["go", "test", "-count=1", "-timeout=30s", "-gcflags=all=-d=checkptr=2", "./..."], self.fixtures / "boundaries")

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
        self.assert_success(["go", "test", "-count=1", "-timeout=30s", "./..."], target)

    @unittest.skipUnless(os.environ.get("SKILLS_RUN_RACE") == "1", "optional race check: set SKILLS_RUN_RACE=1")
    def test_boundaries_race(self):
        self.assert_success(["go", "test", "-race", "-count=1", "-timeout=30s", "./..."], self.fixtures / "boundaries")

    @unittest.skipUnless(os.environ.get("SKILLS_RUN_RACE") == "1", "optional race check: set SKILLS_RUN_RACE=1")
    def test_cleanup_race(self):
        self.assert_success(["go", "test", "-race", "-count=1", "-timeout=30s", "./..."], self.fixtures / "cleanup")


if __name__ == "__main__":
    unittest.main(verbosity=2)
