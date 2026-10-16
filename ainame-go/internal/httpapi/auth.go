package httpapi

import (
	"fmt"
	"net"
	"net/http"
	"net/mail"
	"net/smtp"
	"os"
	"strconv"
	"strings"
	"time"

	"ainame-go/internal/data"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

func registerAuthRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("GET /auth/code", func(w http.ResponseWriter, r *http.Request) {
		email := strings.TrimSpace(r.URL.Query().Get("email"))
		if _, e := mail.ParseAddress(email); e != nil {
			bad(w, "valid email is required")
			return
		}
		code := fmt.Sprintf("%04d", time.Now().UnixNano()%10000)
		if e := sendCode(email, code); e != nil {
			writeJSON(w, 502, map[string]string{"detail": "email delivery failed"})
			return
		}
		row := data.EmailCode{Email: email, Code: code, Type: "test", CreatedTime: time.Now()}
		if e := db.Create(&row).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("POST /auth/register", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			Email           string `json:"email"`
			Username        string `json:"username"`
			Password        string `json:"password"`
			ConfirmPassword string `json:"confirm_password"`
			Code            string `json:"code"`
		}
		if decode(r, &in) != nil {
			bad(w, "invalid JSON")
			return
		}
		in.Email = strings.TrimSpace(in.Email)
		if _, e := mail.ParseAddress(in.Email); e != nil || len(in.Username) < 3 || len(in.Username) > 20 || len(in.Password) < 6 || len(in.Password) > 20 || len(in.ConfirmPassword) < 6 || len(in.ConfirmPassword) > 20 || len(in.Code) != 4 {
			bad(w, "email, username, password or code is invalid")
			return
		}
		if in.Password != in.ConfirmPassword {
			bad(w, "passwords do not match")
			return
		}
		var count int64
		db.Model(&data.User{}).Where("email = ?", in.Email).Count(&count)
		if count > 0 {
			bad(w, "email already registered")
			return
		}
		var code data.EmailCode
		if e := db.Where("email = ? AND code = ?", in.Email, in.Code).Order("id DESC").First(&code).Error; e != nil || time.Since(code.CreatedTime) > 10*time.Minute {
			bad(w, "email or verification code is invalid")
			return
		}
		hash, e := bcrypt.GenerateFromPassword([]byte(in.Password), bcrypt.DefaultCost)
		if e != nil {
			writeJSON(w, 500, map[string]string{"detail": "could not secure password"})
			return
		}
		if e = db.Create(&data.User{Email: in.Email, Username: in.Username, PasswordHash: string(hash)}).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("POST /auth/login", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			Email    string `json:"email"`
			Password string `json:"password"`
		}
		if decode(r, &in) != nil {
			bad(w, "invalid JSON")
			return
		}
		var user data.User
		if e := db.Where("email = ?", strings.TrimSpace(in.Email)).First(&user).Error; e != nil {
			bad(w, "email or password is incorrect")
			return
		}
		if bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(in.Password)) != nil {
			bad(w, "email or password is incorrect")
			return
		}
		secret := os.Getenv("JWT_SECRET")
		if secret == "" {
			secret = "dev-only-change-me-please-use-32chars!!"
		}
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{"iss": strconv.FormatUint(uint64(user.ID), 10), "sub": "1", "exp": time.Now().Add(15 * 24 * time.Hour).Unix()})
		signed, e := token.SignedString([]byte(secret))
		if e != nil {
			writeJSON(w, 500, map[string]string{"detail": "token generation failed"})
			return
		}
		writeJSON(w, 200, map[string]any{"user": map[string]any{"id": user.ID, "email": user.Email, "username": user.Username}, "token": signed})
	})
}
func sendCode(to, code string) error {
	host := os.Getenv("SMTP_HOST")
	if host == "" {
		return fmt.Errorf("SMTP_HOST is not configured")
	}
	port := envString("SMTP_PORT", "587")
	username := os.Getenv("SMTP_USERNAME")
	password := os.Getenv("SMTP_PASSWORD")
	from := envString("SMTP_FROM", username)
	addr := net.JoinHostPort(host, port)
	auth := smtp.PlainAuth("", username, password, host)
	subject := "=?UTF-8?B?" + "5L+h6L+R5Luj56CB" + "?="
	body := fmt.Sprintf("From: %s\r\nTo: %s\r\nSubject: %s\r\nMIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\nYour verification code is %s. It is valid for 10 minutes.\r\n", from, to, subject, code)
	return smtp.SendMail(addr, auth, from, []string{to}, []byte(body))
}

func envString(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}

func mailTest(w http.ResponseWriter, r *http.Request) {
	email := strings.TrimSpace(r.URL.Query().Get("email"))
	if _, err := mail.ParseAddress(email); err != nil {
		bad(w, "valid email is required")
		return
	}
	if err := sendPlainMail(email, "hello", "hello "+email); err != nil {
		writeJSON(w, http.StatusBadGateway, map[string]string{"detail": "email delivery failed"})
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"message": "email sent successfully"})
}

func sendPlainMail(to, subject, text string) error {
	host := os.Getenv("SMTP_HOST")
	if host == "" {
		return fmt.Errorf("SMTP_HOST is not configured")
	}
	username := os.Getenv("SMTP_USERNAME")
	password := os.Getenv("SMTP_PASSWORD")
	from := envString("SMTP_FROM", username)
	addr := net.JoinHostPort(host, envString("SMTP_PORT", "587"))
	auth := smtp.PlainAuth("", username, password, host)
	body := fmt.Sprintf("From: %s\r\nTo: %s\r\nSubject: %s\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n%s\r\n", from, to, subject, text)
	return smtp.SendMail(addr, auth, from, []string{to}, []byte(body))
}
