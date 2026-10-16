package data

import (
	"fmt"
	"os"
	"time"

	"github.com/redis/go-redis/v9"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func OpenRedis() *redis.Client {
	return redis.NewClient(&redis.Options{
		Addr:     env("REDIS_ADDR", "127.0.0.1:6379"),
		Password: os.Getenv("REDIS_PASSWORD"),
		DB:       0,
	})
}
func Open() (*gorm.DB, error) {
	host := env("DB_HOST", "127.0.0.1")
	port := env("DB_PORT", "3306")
	user := env("DB_USER", "root")
	pass := env("DB_PASSWORD", "root")
	dbname := env("DB_NAME", "zhiliao_ainame")
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?charset=utf8mb4&parseTime=True&loc=Local", user, pass, host, port, dbname)
	level := logger.Warn
	if env("APP_ENV", "development") == "development" {
		level = logger.Info
	}
	db, err := gorm.Open(mysql.Open(dsn), &gorm.Config{Logger: logger.Default.LogMode(level)})
	if err != nil {
		return nil, err
	}
	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}
	sqlDB.SetMaxOpenConns(25)
	sqlDB.SetMaxIdleConns(5)
	sqlDB.SetConnMaxLifetime(5 * time.Minute)
	if env("AUTO_MIGRATE", "false") == "true" {
		if err := db.AutoMigrate(&User{}, &EmailCode{}, &Art{}, &School{}, &Teacher{}, &Student{}, &Course{}, &StudentCourse{}, &Company{}, &Product{}, &Order{}, &OrderProduct{}); err != nil {
			return nil, err
		}
	}
	return db, nil
}
func env(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
