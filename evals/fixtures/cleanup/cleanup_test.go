package cleanup

import (
	"encoding/json"
	"errors"
	"io"
	"reflect"
	"strings"
	"testing"
)

func TestLoadDiscardsPartialValue(t *testing.T) {
	value, err := Load(false)
	if value != 0 || err != ErrMissing {
		t.Fatalf("Load(false) = (%d, %v), want (0, ErrMissing)", value, err)
	}
	value, err = Load(true)
	if value != 42 || err != nil {
		t.Fatalf("Load(true) = (%d, %v), want (42, nil)", value, err)
	}
}

func TestRunRecordsWorkError(t *testing.T) {
	failure := errors.New("work failure")
	for _, want := range []error{nil, failure} {
		var recorded error
		calls := 0
		got := Run(func() error { return want }, func(err error) {
			recorded = err
			calls++
		})
		if got != want || recorded != want || calls != 1 {
			t.Fatalf("return=%v recorded=%v calls=%d, want %v once", got, recorded, calls, want)
		}
	}
}

func TestRunRecordsDuringPanic(t *testing.T) {
	wantPanic := &struct {
		message string
	}{message: "work panic"}
	var recovered any
	recorded := errors.New("record not called")
	calls := 0
	returned := false
	var order []string
	func() {
		defer func() {
			recovered = recover()
			order = append(order, "recover")
		}()
		Run(func() error {
			defer func() { order = append(order, "work defer") }()
			panic(wantPanic)
		}, func(err error) {
			recorded = err
			calls++
			order = append(order, "record")
		})
		returned = true
	}()
	if recovered != wantPanic || returned {
		t.Fatalf("panic=%v returned=%v, want unchanged panic and no return", recovered, returned)
	}
	if recorded != nil || calls != 1 {
		t.Fatalf("recorded=%v calls=%d, want nil exactly once", recorded, calls)
	}
	if want := []string{"work defer", "record", "recover"}; !reflect.DeepEqual(order, want) {
		t.Fatalf("unwind order=%v, want %v", order, want)
	}
}

func TestFirstIsOnePreservesShortCircuit(t *testing.T) {
	cases := []struct {
		values []int
		want   bool
	}{
		{values: nil, want: false},
		{values: []int{}, want: false},
		{values: []int{0}, want: false},
		{values: []int{1}, want: true},
	}
	for _, tc := range cases {
		if got := FirstIsOne(tc.values); got != tc.want {
			t.Fatalf("FirstIsOne(%v) = %v, want %v", tc.values, got, tc.want)
		}
	}
}

func TestEmptyIDsMarshalAsNull(t *testing.T) {
	ids := EmptyIDs()
	data, err := json.Marshal(ids)
	if err != nil {
		t.Fatal(err)
	}
	if ids != nil || string(data) != "null" {
		t.Fatalf("got IDs=%v JSON=%s, want nil and null", ids, data)
	}
}

func TestCopyBytesPreservesOwnershipAndNil(t *testing.T) {
	if CopyBytes(nil) != nil {
		t.Fatal("nil input must remain nil")
	}
	if got := CopyBytes([]byte{}); got == nil || len(got) != 0 {
		t.Fatal("allocated empty input must remain allocated empty")
	}
	original := []byte{1, 2}
	copied := CopyBytes(original)
	original[0] = 9
	if len(copied) != 2 || copied[0] != 1 || copied[1] != 2 {
		t.Fatalf("copy changed with source: %v", copied)
	}
	copied[1] = 8
	if original[1] != 2 {
		t.Fatal("copy aliases source")
	}
}

func TestCopyBytesPreservesExactCapacity(t *testing.T) {
	cases := []struct {
		name string
		data []byte
	}{
		{name: "nil", data: nil},
		{name: "allocated empty", data: []byte{}},
		{name: "empty with spare capacity", data: make([]byte, 0, 16)},
		{name: "one byte with spare capacity", data: make([]byte, 1, 16)},
		{name: "three bytes with spare capacity", data: make([]byte, 3, 16)},
		{name: "exact input capacity", data: []byte{1, 2, 3}},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := CopyBytes(tc.data)
			if len(got) != len(tc.data) || cap(got) != len(tc.data) {
				t.Fatalf("length=%d capacity=%d, want both %d", len(got), cap(got), len(tc.data))
			}
			if (got == nil) != (tc.data == nil) {
				t.Fatal("nil versus allocated empty changed")
			}
		})
	}
}

func TestNormalizeName(t *testing.T) {
	cases := []struct {
		input string
		want  string
	}{
		{input: "", want: ""},
		{input: " \tA B\n", want: "A B"},
		{input: "\u3000游戏\u3000", want: "游戏"},
	}
	for _, tc := range cases {
		if got := NormalizeName(tc.input); got != tc.want {
			t.Fatalf("NormalizeName(%q) = %q, want %q", tc.input, got, tc.want)
		}
	}
}

type partialReader struct{}

func (partialReader) Read(data []byte) (int, error) {
	return copy(data, "x"), io.EOF
}

func TestRelayPreservesPartialValueAndEOF(t *testing.T) {
	data := make([]byte, 1)
	n, err := Relay(partialReader{}, data)
	if n != 1 || data[0] != 'x' || err != io.EOF {
		t.Fatalf("Relay = (%d, %v, %q), want (1, EOF, x)", n, err, data)
	}
}

func TestOneShotCompletes(t *testing.T) {
	if got := OneShot(4); got != 5 {
		t.Fatalf("OneShot(4) = %d, want 5", got)
	}
}

func TestTypedNilContract(t *testing.T) {
	err := TypedNil()
	if err == nil || err.Error() != "typed nil failure" {
		t.Fatalf("typed nil contract lost: %v", err)
	}
	value := reflect.ValueOf(err)
	if value.Kind() != reflect.Ptr || !value.IsNil() {
		t.Fatal("expected a nil pointer inside a non-nil error interface")
	}
}

func TestCallSiteIdentity(t *testing.T) {
	if got := CallSite(); !strings.HasSuffix(got, ".CallSite") {
		t.Fatalf("CallSite identity changed to %q", got)
	}
}
