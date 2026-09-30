package sample

import (
	"database/sql"
	_ "example.com/driver"
)

func open() (*sql.DB, error) { return sql.Open("evaldriver", "dsn") }
