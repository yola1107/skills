package sample

import (
	"database/sql"
	_ "github.com/go-sql-driver/mysql"
)

func open() (*sql.DB, error) { return sql.Open("mysql", "dsn") }
