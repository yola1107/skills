package typednil

import "testing"

func TestRunNil(t *testing.T) {
	if err := run(true); err != nil {
		t.Fatalf("run(true) = %#v, want nil", err)
	}
}
