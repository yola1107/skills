// Package boundaries contains correct contracts for review and cleanup evaluations.
package boundaries

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"time"
)

const maxReportBytes = 1024

// NewReportClient refuses redirects. Production callers supply a trusted transport
// and an approved endpoint; this alone is not a general DNS/egress SSRF defense.
func NewReportClient(transport http.RoundTripper) *http.Client {
	return &http.Client{
		Transport: transport,
		Timeout:   5 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
}

// FetchReport accepts only HTTP 200 and at most maxReportBytes from an approved
// endpoint. It discards failed partial results and owns the response Body.
func FetchReport(ctx context.Context, client *http.Client, endpoint string) ([]byte, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return nil, err
	}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close() // Read-only response cleanup; Close errors are best effort.
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected report status: %d", resp.StatusCode)
	}
	data, err := io.ReadAll(io.LimitReader(resp.Body, maxReportBytes+1))
	if err != nil {
		return nil, err
	}
	if len(data) > maxReportBytes {
		return nil, errors.New("report too large")
	}
	return data, nil
}

// ScanLines borrows r and preserves partial lines and Scanner's terminal error.
func ScanLines(r io.Reader) ([]string, error) {
	scanner := bufio.NewScanner(r)
	var lines []string
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}
	return lines, scanner.Err()
}

// Rows is the lifecycle subset of sql.Rows needed by CountRows.
type Rows interface {
	Next() bool
	Err() error
	Close() error
}

// CountRows takes ownership of rows and preserves its terminal error and count.
// Close is best-effort cleanup for this read-only operation.
func CountRows(rows Rows) (int, error) {
	defer rows.Close()
	count := 0
	for rows.Next() {
		count++
	}
	return count, rows.Err()
}

// WriteAudit records token presence, never the credential value.
func WriteAudit(w io.Writer, token string) error {
	event := struct {
		Event        string `json:"event"`
		TokenPresent bool   `json:"token_present"`
	}{
		Event:        "session_check",
		TokenPresent: token != "",
	}
	return json.NewEncoder(w).Encode(event)
}
