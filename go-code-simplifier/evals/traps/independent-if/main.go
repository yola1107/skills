package independentif

func actions(a, b bool) []string {
	var out []string
	if a {
		out = append(out, "a")
	}
	if b {
		out = append(out, "b")
	}
	return out
}
