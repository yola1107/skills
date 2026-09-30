package reflectdedup

type User struct{ Name string }
type Team struct{ Name string }

func userName(v User) string { return v.Name }
func teamName(v Team) string { return v.Name }
