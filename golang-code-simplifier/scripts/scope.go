//go:build ignore

// Scope lists the hand-written Go files to simplify and the packages to verify,
// grouped by module. Generated files and vendor/testdata directories are skipped.
//
// Run it from anywhere inside a git repository:
//
//	go run scope.go            # files changed relative to HEAD, plus untracked files
//	go run scope.go <path>...  # all Go files under the given files or directories
package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
)

var generatedRE = regexp.MustCompile(`^// Code generated .* DO NOT EDIT\.$`)

func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, "scope:", err)
		os.Exit(1)
	}
}

func run(args []string) error {
	out, err := git(".", "rev-parse", "--show-toplevel")
	if err != nil {
		return err
	}
	root := filepath.Clean(strings.TrimSpace(out))

	var files []string
	if len(args) > 0 {
		files, err = walkPaths(args)
	} else {
		files, err = changedFiles(root)
	}
	if err != nil {
		return err
	}

	byModule := make(map[string][]string)
	var noModule []string
	for _, f := range files {
		ok, err := isHandWritten(f)
		if err != nil {
			return err
		}
		if !ok {
			continue
		}
		mod := findModule(filepath.Dir(f))
		if mod == "" {
			noModule = append(noModule, f)
			continue
		}
		byModule[mod] = append(byModule[mod], f)
	}

	if len(byModule) == 0 && len(noModule) == 0 {
		fmt.Println("no hand-written Go files in scope")
		return nil
	}

	mods := make([]string, 0, len(byModule))
	for m := range byModule {
		mods = append(mods, m)
	}
	sort.Strings(mods)
	for _, m := range mods {
		printModule(m, byModule[m])
	}
	if len(noModule) > 0 {
		fmt.Println("files outside any module (not verified):")
		for _, f := range noModule {
			fmt.Println("  " + filepath.ToSlash(f))
		}
	}
	return nil
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

// changedFiles returns absolute paths of existing Go files that differ from
// HEAD or are untracked. In a repository without commits it returns all
// tracked and untracked Go files.
func changedFiles(root string) ([]string, error) {
	changed, err := git(root, "diff", "-z", "--name-only", "HEAD")
	if err != nil {
		changed, err = git(root, "ls-files", "-z")
		if err != nil {
			return nil, err
		}
	}
	untracked, err := git(root, "ls-files", "-z", "--others", "--exclude-standard")
	if err != nil {
		return nil, err
	}

	seen := make(map[string]bool)
	var files []string
	for _, name := range strings.Split(changed+untracked, "\x00") {
		if !strings.HasSuffix(name, ".go") || seen[name] {
			continue
		}
		seen[name] = true
		path := filepath.Join(root, filepath.FromSlash(name))
		if info, err := os.Stat(path); err != nil || info.IsDir() {
			continue
		}
		if skippedDir(filepath.Dir(name)) {
			continue
		}
		files = append(files, path)
	}
	sort.Strings(files)
	return files, nil
}

func walkPaths(paths []string) ([]string, error) {
	var files []string
	for _, p := range paths {
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
			if strings.HasSuffix(path, ".go") {
				files = append(files, path)
			}
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	sort.Strings(files)
	return files, nil
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

// isHandWritten reports whether the file lacks the standard generated-code
// header, which must appear before the package clause.
func isHandWritten(path string) (bool, error) {
	f, err := os.Open(path)
	if err != nil {
		return false, err
	}
	defer f.Close()

	sc := bufio.NewScanner(f)
	sc.Buffer(make([]byte, 0, 64*1024), 1024*1024)
	for sc.Scan() {
		line := strings.TrimRight(sc.Text(), "\r")
		if generatedRE.MatchString(line) {
			return false, nil
		}
		if strings.HasPrefix(line, "package ") {
			break
		}
	}
	return true, sc.Err()
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

func printModule(mod string, files []string) {
	pkgSet := make(map[string]bool)
	relFiles := make([]string, 0, len(files))
	for _, f := range files {
		rel, _ := filepath.Rel(mod, f)
		relFiles = append(relFiles, filepath.ToSlash(rel))
		pkg := "./" + filepath.ToSlash(filepath.Dir(rel))
		if pkg == "./." {
			pkg = "."
		}
		pkgSet[pkg] = true
	}
	pkgs := make([]string, 0, len(pkgSet))
	for p := range pkgSet {
		pkgs = append(pkgs, p)
	}
	sort.Strings(pkgs)

	fileList := strings.Join(relFiles, " ")
	pkgList := strings.Join(pkgs, " ")
	fmt.Printf("module: %s\n", filepath.ToSlash(mod))
	fmt.Println("files:")
	for _, f := range relFiles {
		fmt.Println("  " + f)
	}
	fmt.Println("packages:")
	for _, p := range pkgs {
		fmt.Println("  " + p)
	}
	fmt.Println("verify (run in module directory):")
	fmt.Println("  gofmt -l " + fileList)
	fmt.Println("  go build " + pkgList)
	fmt.Println("  go vet " + pkgList)
	fmt.Println("  go test " + pkgList)
	fmt.Println()
}
