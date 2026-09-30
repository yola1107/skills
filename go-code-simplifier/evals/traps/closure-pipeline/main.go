package closurepipeline

func process(v int) int {
	v = v + 1
	v = v * 2
	if v > 10 {
		v = 10
	}
	return v
}
