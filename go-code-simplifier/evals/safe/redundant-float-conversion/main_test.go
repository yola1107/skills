package redundantfloat

import "testing"

func TestValue(t *testing.T) {
	if value() != float64(0.1) {
		t.Fatalf("value() = %v", value())
	}
}
