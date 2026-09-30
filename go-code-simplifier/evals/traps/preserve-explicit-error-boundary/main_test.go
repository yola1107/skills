package errorboundary

import (
	"errors"
	"testing"
)

func TestNilSuccessStillMapsToMissing(t *testing.T) {
	_, err := value(1)
	if !errors.Is(err, errMissing) {
		t.Fatalf("value(1) error = %v, want errMissing", err)
	}
}
