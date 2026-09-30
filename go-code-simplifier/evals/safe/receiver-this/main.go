package receiverthis

type Server struct {
	name string
}

func (this *Server) Name() string {
	return this.name
}

func (this *Server) Empty() bool {
	return this.name == ""
}
