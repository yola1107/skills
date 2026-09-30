package driver

import (
	"database/sql"
	sqldriver "database/sql/driver"
	"errors"
)

type d struct{}

func (d) Open(string) (sqldriver.Conn, error) { return nil, errors.New("not implemented") }

func init() { sql.Register("evaldriver", d{}) }
