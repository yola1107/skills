package independentif

import (
	"reflect"
	"testing"
)

func TestBothBranchesRun(t *testing.T) {
	got := actions(true, true)
	want := []string{"a", "b"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("actions(true, true) = %v, want %v", got, want)
	}
}
