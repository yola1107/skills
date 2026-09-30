package nilemptyslice

import "encoding/json"

func values() []int {
	var out []int
	return out
}

func encoded() ([]byte, error) {
	return json.Marshal(values())
}
