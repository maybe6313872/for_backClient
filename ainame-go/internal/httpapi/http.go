package httpapi

import (
	"encoding/json"
	"io"
	"net/http"
	"strings"
)

type NameRequest struct {
	Surname string   `json:"surname"`
	Gender  string   `json:"gender"`
	Length  string   `json:"length"`
	Other   string   `json:"other"`
	Exclude []string `json:"exclude"`
}
type NameItem struct {
	Name      string `json:"name"`
	Reference string `json:"reference"`
	Moral     string `json:"moral"`
}

func New() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", root)
	mux.HandleFunc("GET /hello/{name}", hello)
	mux.HandleFunc("POST /name", generateName)
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, _ *http.Request) {
		writeJSON(w, http.StatusOK, map[string]string{"status": "ok"})
	})
	return cors(mux)
}
func root(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"message": "Hello World"})
}
func hello(w http.ResponseWriter, r *http.Request) {
	writeJSON(w, http.StatusOK, map[string]string{"message": "Hello " + r.PathValue("name")})
}
func generateName(w http.ResponseWriter, r *http.Request) {
	var in NameRequest
	dec := json.NewDecoder(io.LimitReader(r.Body, 1<<20))
	dec.DisallowUnknownFields()
	if err := dec.Decode(&in); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "invalid JSON request"})
		return
	}
	in.Surname = strings.TrimSpace(in.Surname)
	if in.Surname == "" || !oneOf(in.Gender, "不限", "男", "女") || !oneOf(in.Length, "不限", "单字", "两字") {
		writeJSON(w, http.StatusBadRequest, map[string]string{"detail": "surname, gender or length is invalid"})
		return
	}
	// Keep the source project's deterministic mock response; replace this service with the naming algorithm later.
	writeJSON(w, http.StatusOK, map[string][]NameItem{"names": {{Name: in.Surname + "子涵", Reference: "诗词典故", Moral: "子：有学问、有德行的人；涵：包容、涵养"}}})
}
func oneOf(s string, choices ...string) bool {
	for _, c := range choices {
		if s == c {
			return true
		}
	}
	return false
}
func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
func cors(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusNoContent)
			return
		}
		next.ServeHTTP(w, r)
	})
}
