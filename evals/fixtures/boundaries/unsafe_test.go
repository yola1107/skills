package boundaries

import "testing"

func TestWordAtPreservesAliasAndBounds(t *testing.T) {
	words := [2]uint32{10, 20}
	for i := range words {
		ptr := WordAt(&words, i)
		if ptr != &words[i] {
			t.Fatalf("index %d does not alias original element", i)
		}
		*ptr = uint32(i + 100)
		if words[i] != uint32(i+100) {
			t.Fatalf("index %d mutation was lost", i)
		}
	}
	if WordAt(nil, 0) != nil || WordAt(&words, -1) != nil || WordAt(&words, len(words)) != nil {
		t.Fatal("invalid input did not return nil")
	}
}
