package typedconstant

const limit int8 = 100

func use(v int8) int8 { return v }

func value() int8 { return use(limit) }
