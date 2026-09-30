package explicitiota

const (
	statusOK = 1
	statusBad = 2
	statusPending = 3
)

func values() [3]int { return [3]int{statusOK, statusBad, statusPending} }
