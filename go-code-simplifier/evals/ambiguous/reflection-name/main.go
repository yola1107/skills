package reflectionname

type Handler struct{}

func (h *Handler) Process() {}

func methodName() string { return "Process" }
