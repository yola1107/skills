package redundantreturn

func twice(v int) int { return v * 2 }

func value(v int) int {
	result := twice(v)
	return result
}
