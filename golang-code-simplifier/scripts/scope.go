//go:build ignore

// Scope lists the hand-written Go files to simplify and the packages to verify,
// grouped by module. Generated files and vendor/testdata directories are skipped.
// It also reports files with CRLF line endings and test functions that appear
// to reach external services, so they can be excluded with go test -skip.
//
// Run it from anywhere inside a git repository:
//
//	go run scope.go            # files changed relative to HEAD, plus untracked files
//	go run scope.go <path>...  # all Go files under the given files or directories
package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"slices"
	"sort"
	"strings"
)

var (
	generatedRE = regexp.MustCompile(`^// Code generated .* DO NOT EDIT\.$`)
	// externalRE matches DSNs, URLs and IPv4 addresses that suggest a test
	// talks to a database, network service or third-party API.
	externalRE   = regexp.MustCompile(`tcp\([^)]*\)|[a-zA-Z][a-zA-Z0-9+.-]*://[^\s"'/]*|\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b`)
	localRE      = regexp.MustCompile(`localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\]`)
	credentialRE = regexp.MustCompile(`([^:/@\s"'(]+):([^@\s"']+)@`)
)

type module struct {
	files   []goFile
	deleted []string
}

type goFile struct {
	path     string
	crlf     bool
	external []externalTest
}

type externalTest struct {
	name string
	line int
	text string
}

func main() {
	if err := run(os.Stdout, ".", os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, "scope:", err)
		os.Exit(1)
	}
}

// run resolves relative paths in args against dir.
func run(w io.Writer, dir string, args []string) error {
	out, err := git(dir, "rev-parse", "--show-toplevel")
	if err != nil {
		return err
	}
	root := filepath.Clean(strings.TrimSpace(out))

	var paths, deleted []string
	if len(args) > 0 {
		paths, err = walkPaths(root, dir, args)
	} else {
		paths, deleted, err = changedFiles(root)
	}
	if err != nil {
		return err
	}

	modules := make(map[string]*module)
	moduleFor := func(path string) *module {
		dir := findModule(filepath.Dir(path))
		if dir == "" {
			return nil
		}
		if modules[dir] == nil {
			modules[dir] = &module{}
		}
		return modules[dir]
	}
	var noModule []string
	for _, p := range paths {
		f, ok, err := inspect(p)
		if err != nil {
			return err
		}
		if !ok {
			continue
		}
		m := moduleFor(p)
		if m == nil {
			noModule = append(noModule, p)
			continue
		}
		m.files = append(m.files, f)
	}
	for _, p := range deleted {
		if m := moduleFor(p); m != nil {
			m.deleted = append(m.deleted, p)
		}
	}

	if len(modules) == 0 && len(noModule) == 0 {
		fmt.Fprintln(w, "no hand-written Go files in scope")
		return nil
	}

	dirs := make([]string, 0, len(modules))
	for d := range modules {
		dirs = append(dirs, d)
	}
	sort.Strings(dirs)
	for _, d := range dirs {
		printModule(w, d, modules[d])
	}
	printList(w, "files outside any module (not verified):", toSlash(noModule))
	return nil
}

func toSlash(paths []string) []string {
	out := make([]string, len(paths))
	for i, p := range paths {
		out[i] = filepath.ToSlash(p)
	}
	return out
}

func git(dir string, args ...string) (string, error) {
	cmd := exec.Command("git", append([]string{"-C", dir}, args...)...)
	var stderr bytes.Buffer
	cmd.Stderr = &stderr
	out, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("git %s: %v: %s", strings.Join(args, " "), err, strings.TrimSpace(stderr.String()))
	}
	return string(out), nil
}

// changedFiles returns absolute paths of Go files that differ from HEAD or are
// untracked, split into existing and deleted files. Renames are reported as a
// deletion plus an addition so the old package is verified too. In a
// repository without commits it returns all tracked and untracked Go files.
func changedFiles(root string) (files, deleted []string, err error) {
	changed, err := git(root, "diff", "-z", "--name-only", "--no-renames", "HEAD")
	if err != nil {
		changed, err = git(root, "ls-files", "-z")
		if err != nil {
			return nil, nil, err
		}
	}
	untracked, err := git(root, "ls-files", "-z", "--others", "--exclude-standard")
	if err != nil {
		return nil, nil, err
	}

	seen := make(map[string]bool)
	for _, name := range strings.Split(changed+untracked, "\x00") {
		if !strings.HasSuffix(name, ".go") || seen[name] || skippedDir(filepath.Dir(name)) {
			continue
		}
		seen[name] = true
		path := filepath.Join(root, filepath.FromSlash(name))
		info, err := os.Stat(path)
		switch {
		case os.IsNotExist(err):
			deleted = append(deleted, path)
		case err != nil:
			return nil, nil, err
		case !info.IsDir():
			files = append(files, path)
		}
	}
	sort.Strings(files)
	sort.Strings(deleted)
	return files, deleted, nil
}

// walkPaths returns the Go files under paths, resolving relative paths
// against base. The exclusion rules apply to the given paths themselves, not
// only to the directories found while walking.
func walkPaths(root, base string, paths []string) ([]string, error) {
	var files []string
	for _, p := range paths {
		if !filepath.IsAbs(p) {
			p = filepath.Join(base, p)
		}
		abs, err := filepath.Abs(p)
		if err != nil {
			return nil, err
		}
		err = filepath.WalkDir(abs, func(path string, d fs.DirEntry, err error) error {
			if err != nil {
				return err
			}
			if d.IsDir() {
				if path != abs && skippedDir(d.Name()) {
					return filepath.SkipDir
				}
				return nil
			}
			if !strings.HasSuffix(path, ".go") {
				return nil
			}
			if rel, err := filepath.Rel(root, path); err == nil && skippedDir(filepath.Dir(rel)) {
				return nil
			}
			files = append(files, path)
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	sort.Strings(files)
	return files, nil
}

func hasGoFiles(dir string) bool {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return false
	}
	for _, e := range entries {
		if !e.IsDir() && strings.HasSuffix(e.Name(), ".go") {
			return true
		}
	}
	return false
}

// skippedDir reports whether any element of dir is ignored by the go tool or
// holds code that should not be simplified.
func skippedDir(dir string) bool {
	for _, elem := range strings.Split(filepath.ToSlash(dir), "/") {
		if elem == "vendor" || elem == "testdata" ||
			(len(elem) > 1 && (elem[0] == '.' || elem[0] == '_') && elem != "..") {
			return true
		}
	}
	return false
}

// inspect reads the file once and reports ok=false for generated code, whose
// standard header must appear before the package clause.
func inspect(path string) (goFile, bool, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return goFile{}, false, err
	}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimRight(line, "\r")
		if generatedRE.MatchString(line) {
			return goFile{}, false, nil
		}
		if strings.HasPrefix(line, "package ") {
			break
		}
	}

	f := goFile{path: path, crlf: bytes.Contains(data, []byte("\r\n"))}
	if strings.HasSuffix(path, "_test.go") {
		f.external = externalTests(path, data)
	}
	return f, true, nil
}

// externalTests returns the test, benchmark, fuzz and example functions whose
// bodies mention a non-local address. Files that fail to parse are skipped;
// go build and go vet will report them.
func externalTests(path string, data []byte) []externalTest {
	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, path, data, parser.ParseComments)
	if err != nil {
		return nil
	}

	var found []externalTest
	for _, decl := range file.Decls {
		fn, ok := decl.(*ast.FuncDecl)
		if !ok || fn.Recv != nil || fn.Body == nil || !isTestFunc(fn.Name.Name) {
			continue
		}
		start := fset.Position(fn.Body.Pos())
		end := fset.Position(fn.Body.End())
		lines := strings.Split(string(data[start.Offset:end.Offset]), "\n")
		for i, line := range lines {
			if !mentionsExternal(line) {
				continue
			}
			found = append(found, externalTest{
				name: fn.Name.Name,
				line: start.Line + i,
				text: snippet(line),
			})
			break
		}
	}
	return found
}

func isTestFunc(name string) bool {
	for _, prefix := range []string{"Test", "Benchmark", "Fuzz", "Example"} {
		if strings.HasPrefix(name, prefix) && name != "TestMain" {
			return true
		}
	}
	return false
}

func mentionsExternal(line string) bool {
	for _, m := range externalRE.FindAllString(line, -1) {
		if !localRE.MatchString(m) {
			return true
		}
	}
	return false
}

// snippet trims the line and masks user:password@ credentials.
func snippet(line string) string {
	s := credentialRE.ReplaceAllString(strings.TrimSpace(line), "$1:***@")
	if r := []rune(s); len(r) > 100 {
		s = string(r[:100]) + "..."
	}
	return s
}

func findModule(dir string) string {
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return ""
		}
		dir = parent
	}
}

// printModule prints the scope of one module. Deleting or moving a file can
// break importers anywhere in the module, so build and vet then cover ./...
func printModule(w io.Writer, mod string, m *module) {
	rel := func(p string) string {
		r, _ := filepath.Rel(mod, p)
		return filepath.ToSlash(r)
	}
	pkgOf := func(relPath string) string {
		pkg := "./" + filepath.ToSlash(filepath.Dir(relPath))
		if pkg == "./." {
			pkg = "."
		}
		return pkg
	}

	pkgSet := make(map[string]bool)
	var relFiles, relDeleted, removedPkgs, crlfFiles, skipNames []string
	var external []string
	for _, p := range m.deleted {
		r := rel(p)
		relDeleted = append(relDeleted, r)
		if hasGoFiles(filepath.Dir(p)) {
			pkgSet[pkgOf(r)] = true
		} else {
			removedPkgs = append(removedPkgs, pkgOf(r))
		}
	}
	for _, f := range m.files {
		r := rel(f.path)
		relFiles = append(relFiles, r)
		pkgSet[pkgOf(r)] = true
		if f.crlf {
			crlfFiles = append(crlfFiles, r)
		}
		for _, t := range f.external {
			external = append(external, fmt.Sprintf("%s:%d %s: %s", r, t.line, t.name, t.text))
			skipNames = append(skipNames, regexp.QuoteMeta(t.name))
		}
	}
	pkgs := make([]string, 0, len(pkgSet))
	for p := range pkgSet {
		pkgs = append(pkgs, p)
	}
	sort.Strings(pkgs)
	sort.Strings(removedPkgs)
	removedPkgs = slices.Compact(removedPkgs)

	pkgList := strings.Join(pkgs, " ")
	buildList := pkgList
	if len(relDeleted) > 0 {
		buildList = "./..."
	}
	testArgs := pkgList
	if len(skipNames) > 0 {
		testArgs = fmt.Sprintf("-skip '^(%s)$' %s", strings.Join(skipNames, "|"), pkgList)
	}

	fmt.Fprintf(w, "module: %s\n", filepath.ToSlash(mod))
	printList(w, "files:", relFiles)
	printList(w, "deleted files (importers may break; build and vet cover ./...):", relDeleted)
	printList(w, "packages:", pkgs)
	printList(w, "removed packages (no Go files left):", removedPkgs)
	printList(w, "crlf files (convert back to CRLF after gofmt):", crlfFiles)
	printList(w, "tests that may reach external services (confirm, then exclude):", external)
	fmt.Fprintln(w, "verify (run in module directory):")
	if len(relFiles) > 0 {
		fmt.Fprintln(w, "  gofmt -l "+strings.Join(relFiles, " "))
	}
	fmt.Fprintln(w, "  go build "+buildList)
	fmt.Fprintln(w, "  go vet "+buildList)
	if len(pkgs) > 0 {
		fmt.Fprintln(w, "  go test "+testArgs)
	}
	fmt.Fprintln(w)
}

func printList(w io.Writer, title string, items []string) {
	if len(items) == 0 {
		return
	}
	fmt.Fprintln(w, title)
	for _, item := range items {
		fmt.Fprintln(w, "  "+item)
	}
}
