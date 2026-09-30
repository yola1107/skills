package sample

type Store struct{ values map[int]string }

func (s *Store) value(id int) string { return s.values[id] }
