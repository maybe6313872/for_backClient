package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"ainame-go/internal/data"
	"ainame-go/internal/httpapi"
)

func main() {
	db, err := data.Open()
	if err != nil {
		log.Fatalf("connect MySQL: %v", err)
	}
	redisClient := data.OpenRedis()
	if err := redisClient.Ping(context.Background()).Err(); err != nil {
		log.Fatalf("connect Redis: %v", err)
	}
	addr := ":" + env("PORT", "5029")
	server := &http.Server{
		Addr:              addr,
		Handler:           httpapi.NewWithDB(db, redisClient),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       15 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	log.Printf("ainame-go listening on %s", addr)
	log.Fatal(server.ListenAndServe())
}

func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
