package errorboundary

import "errors"

var errMissing = errors.New("missing")

func lookup(ok bool) (*int, error) {
	if !ok {
		return nil, errMissing
	}
	v := 1
	return &v, nil
}

func value(ok bool) (int, error) {
	v, err := lookup(ok)
	if err != nil {
		return 0, err
	}
	if v == nil {
		return 0, errMissing
	}
	return *v, nil
}
