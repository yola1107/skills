package boundaries

import (
	"bytes"
	"context"
	"errors"
	"io"
	"net/http"
	"reflect"
	"strings"
	"testing"
)

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(req *http.Request) (*http.Response, error) {
	return f(req)
}

type trackedBody struct {
	io.Reader
	closes int
}

func (b *trackedBody) Close() error {
	b.closes++
	return nil
}

func reportClient(status int, r io.Reader) (*http.Client, *trackedBody) {
	body := &trackedBody{Reader: r}
	client := NewReportClient(roundTripFunc(func(req *http.Request) (*http.Response, error) {
		return &http.Response{StatusCode: status, Body: body, Header: make(http.Header), Request: req}, nil
	}))
	return client, body
}

func TestFetchReportChecksStatusAndCloses(t *testing.T) {
	for _, status := range []int{http.StatusOK, http.StatusNotFound, http.StatusInternalServerError} {
		client, body := reportClient(status, strings.NewReader("report"))
		data, err := FetchReport(context.Background(), client, "https://report.example/item")
		if status == http.StatusOK {
			if err != nil || string(data) != "report" {
				t.Fatalf("status %d: data=%q err=%v", status, data, err)
			}
		} else if err == nil || data != nil {
			t.Fatalf("status %d was not rejected: data=%q err=%v", status, data, err)
		}
		if body.closes != 1 {
			t.Fatalf("status %d: Body closed %d times", status, body.closes)
		}
	}
}

func TestFetchReportLimitsActualBytes(t *testing.T) {
	for _, size := range []int{0, maxReportBytes, maxReportBytes + 1, maxReportBytes * 2} {
		input := strings.NewReader(strings.Repeat("a", size))
		client, body := reportClient(http.StatusOK, input)
		data, err := FetchReport(context.Background(), client, "https://report.example/item")
		if size <= maxReportBytes {
			if err != nil || len(data) != size {
				t.Fatalf("size %d: len=%d err=%v", size, len(data), err)
			}
		} else if err == nil || data != nil {
			t.Fatalf("size %d was accepted or exposed partial data", size)
		}
		if size-input.Len() > maxReportBytes+1 || body.closes != 1 {
			t.Fatalf("size %d: unbounded read or Body not closed", size)
		}
	}
}

type errorReader struct {
	err error
}

func (r errorReader) Read([]byte) (int, error) { return 0, r.err }

func TestFetchReportPreservesReadError(t *testing.T) {
	want := errors.New("read interrupted")
	client, body := reportClient(http.StatusOK, io.MultiReader(strings.NewReader("partial"), errorReader{err: want}))
	data, err := FetchReport(context.Background(), client, "https://report.example/item")
	if err != want || data != nil || body.closes != 1 {
		t.Fatalf("data=%q err=%v closes=%d", data, err, body.closes)
	}
}

func TestReportClientRefusesRedirects(t *testing.T) {
	calls := 0
	body := &trackedBody{Reader: strings.NewReader("redirect")}
	client := NewReportClient(roundTripFunc(func(req *http.Request) (*http.Response, error) {
		calls++
		if calls > 1 {
			return &http.Response{StatusCode: http.StatusOK, Body: io.NopCloser(strings.NewReader("unexpected")), Header: make(http.Header), Request: req}, nil
		}
		return &http.Response{
			StatusCode: http.StatusFound,
			Body:       body,
			Header:     http.Header{"Location": []string{"https://other.example/item"}},
			Request:    req,
		}, nil
	}))
	data, err := FetchReport(context.Background(), client, "https://report.example/item")
	if err == nil || data != nil || calls != 1 || body.closes != 1 {
		t.Fatalf("data=%q err=%v requests=%d closes=%d", data, err, calls, body.closes)
	}
}

func TestScanLinesPreservesTerminalError(t *testing.T) {
	want := errors.New("scan interrupted")
	lines, err := ScanLines(io.MultiReader(strings.NewReader("one\ntwo\n"), errorReader{err: want}))
	if err != want || !reflect.DeepEqual(lines, []string{"one", "two"}) {
		t.Fatalf("lines=%q err=%v", lines, err)
	}
	lines, err = ScanLines(strings.NewReader("one\ntwo\n"))
	if err != nil || !reflect.DeepEqual(lines, []string{"one", "two"}) {
		t.Fatalf("normal EOF: lines=%q err=%v", lines, err)
	}
	if _, err = ScanLines(strings.NewReader(strings.Repeat("a", 128*1024))); err == nil {
		t.Fatal("oversized scanner token was accepted")
	}
}

type fakeRows struct {
	remaining int
	terminal  error
	closes    int
}

func (r *fakeRows) Next() bool {
	if r.remaining == 0 {
		return false
	}
	r.remaining--
	return true
}

func (r *fakeRows) Err() error { return r.terminal }

func (r *fakeRows) Close() error {
	r.closes++
	return nil
}

func TestCountRowsPreservesTerminalError(t *testing.T) {
	for _, want := range []error{nil, errors.New("rows interrupted")} {
		rows := &fakeRows{remaining: 2, terminal: want}
		n, err := CountRows(rows)
		if n != 2 || err != want || rows.closes != 1 {
			t.Fatalf("count=%d err=%v closes=%d", n, err, rows.closes)
		}
	}
}

func TestWriteAuditDoesNotExposeToken(t *testing.T) {
	var buf bytes.Buffer
	if err := WriteAudit(&buf, "fixture-token-not-a-real-credential"); err != nil {
		t.Fatal(err)
	}
	if got, want := buf.String(), "{\"event\":\"session_check\",\"token_present\":true}\n"; got != want {
		t.Fatalf("unexpected audit output: %q", got)
	}
}
