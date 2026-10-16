package httpapi

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestRoot(t *testing.T) {
	r := httptest.NewRequest(http.MethodGet, "/", nil)
	w := httptest.NewRecorder()
	New().ServeHTTP(w, r)
	if w.Code != 200 || !strings.Contains(w.Body.String(), "Hello World") {
		t.Fatalf("unexpected response: %d %s", w.Code, w.Body.String())
	}
}
func TestNameValidation(t *testing.T) {
	r := httptest.NewRequest(http.MethodPost, "/name", strings.NewReader(`{"surname":"","gender":"男","length":"单字"}`))
	w := httptest.NewRecorder()
	New().ServeHTTP(w, r)
	if w.Code != 400 {
		t.Fatalf("want 400, got %d", w.Code)
	}
}
