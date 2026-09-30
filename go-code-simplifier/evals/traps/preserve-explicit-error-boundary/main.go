package errorboundary

import "errors"

var errMissing = errors.New("missing")

func lookup(mode int) (*int, error) {
	switch mode {
	case 0:
		return nil, errMissing
	case 1:
		return nil, nil
	default:
		v := 1
		return &v, nil
	}
}

func value(mode int) (int, error) {
	v, err := lookup(mode)
	if err != nil {
		return 0, err
	}
	if v == nil {
		return 0, errMissing
	}
	return *v, nil
}
