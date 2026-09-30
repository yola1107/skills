package nilemptyslice

import "testing"

func TestEncodedNilSlice(t *testing.T) {
	got, err := encoded()
	if err != nil {
		t.Fatal(err)
	}
	if string(got) != "null" {
		t.Fatalf("encoded() = %s, want null", got)
	}
}
