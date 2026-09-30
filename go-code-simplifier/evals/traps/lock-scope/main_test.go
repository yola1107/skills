package sample

import "testing"

func TestPublishRunsWhileLocked(t *testing.T) {
	var s State
	s.updateAndPublish(func(int) {
		if s.mu.TryLock() {
			s.mu.Unlock()
			t.Fatal("publish ran without State.mu held")
		}
	})
}
