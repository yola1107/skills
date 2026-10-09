// Package cleanup supplies a fixed input for behavior-preserving skill evaluation.
package cleanup

import (
	"errors"
	"io"
	"runtime"
	"strings"
)

// ErrMissing is returned unchanged when no complete result is available.
var ErrMissing = errors.New("missing")

func lookup(found bool) (int, error) {
	if !found {
		return 7, ErrMissing
	}
	return 42, nil
}

// Load discards partial values on failure.
func Load(found bool) (int, error) {
	value, err := lookup(found)
	if err != nil {
		return 0, err
	}
	return value, nil
}

// Run records the exact work error after work returns.
func Run(work func() error, record func(error)) error {
	var err error
	defer func() { record(err) }()
	err = work()
	return err
}

// FirstIsOne accepts empty and nil input.
func FirstIsOne(values []int) bool {
	return len(values) > 0 && values[0] == 1
}

// EmptyIDs returns a nil slice, which must marshal as JSON null.
func EmptyIDs() []int {
	var ids []int
	return ids
}

// CopyBytes returns an independent copy, preserving nil versus allocated empty.
func CopyBytes(data []byte) []byte {
	if data == nil {
		return nil
	}
	result := make([]byte, len(data))
	copy(result, data)
	return result
}

// NormalizeName trims leading and trailing whitespace without other changes.
func NormalizeName(name string) string {
	trimmedName := strings.TrimSpace(name)
	result := trimmedName
	return result
}

// Relay preserves the Reader's partial result and exact error, including EOF.
func Relay(reader io.Reader, data []byte) (int, error) {
	return reader.Read(data)
}

// OneShot waits for one finite calculation; it owns no longer-lived worker.
func OneShot(value int) int {
	result := make(chan int, 1)
	go func() { result <- value + 1 }()
	return <-result
}

// nilFailure deliberately supports a nil receiver.
type nilFailure struct{}

func (*nilFailure) Error() string {
	return "typed nil failure"
}

// TypedNil deliberately returns a non-nil interface with a nil dynamic value.
func TypedNil() error {
	var err *nilFailure
	return err
}

//go:noinline
func currentCaller() string {
	pc, _, _, ok := runtime.Caller(1)
	if !ok {
		return ""
	}
	fn := runtime.FuncForPC(pc)
	if fn == nil {
		return ""
	}
	return fn.Name()
}

// CallSite returns its own function identity through currentCaller.
//
//go:noinline
func CallSite() string {
	return currentCaller()
}
