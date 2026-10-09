"""Offline repository checks, not model/agent evaluations (Python 3.9+)."""

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
        for name in ("cleanup", "access"):
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

    @unittest.skipUnless(os.environ.get("SKILLS_RUN_RACE") == "1", "optional race check: set SKILLS_RUN_RACE=1")
    def test_cleanup_race(self):
        self.assert_success(["go", "test", "-race", "-count=1", "-timeout=30s", "./..."], self.fixtures / "cleanup")


if __name__ == "__main__":
    unittest.main(verbosity=2)
