package boundaries

import "unsafe"

// WordAt returns an alias inside words, or nil for invalid input. Cleanup may
// use ordinary indexing if it preserves this contract, but may not split the
// uintptr round-trip into separate expressions.
func WordAt(words *[2]uint32, index int) *uint32 {
	if words == nil || index < 0 || index >= len(words) {
		return nil
	}
	ptr := unsafe.Pointer(&words[0])
	return (*uint32)(unsafe.Pointer(uintptr(ptr) + uintptr(index)*unsafe.Sizeof(words[0])))
}
