package sample

import "sync"

type State struct {
	mu sync.Mutex
	n int
}

func (s *State) updateAndPublish(publish func(int)) {
	s.mu.Lock()
	s.n++
	publish(s.n)
	s.mu.Unlock()
}
