package errorflow

import "errors"

var errBad = errors.New("bad")

func run(ok bool) error {
	if !ok {
		return errBad
	} else {
		return nil
	}
}
