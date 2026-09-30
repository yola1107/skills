package typednil

type ValidationError struct{}

func (*ValidationError) Error() string { return "invalid" }

func validate(ok bool) *ValidationError {
	if ok {
		return nil
	}
	return &ValidationError{}
}

func run(ok bool) error {
	err := validate(ok)
	if err != nil {
		return err
	}
	return nil
}
