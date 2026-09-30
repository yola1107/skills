package sample

import "testing"

func TestDriverRegisteredByBlankImport(t *testing.T) {
	db, err := open()
	if err != nil {
		t.Fatalf("open() = %v", err)
	}
	_ = db.Close()
}
