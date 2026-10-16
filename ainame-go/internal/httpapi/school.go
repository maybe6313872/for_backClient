package httpapi

import (
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"ainame-go/internal/data"
	"github.com/redis/go-redis/v9"
	"gorm.io/gorm"
)

type result struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    any    `json:"data,omitempty"`
}

func NewWithDB(db *gorm.DB, redisClient *redis.Client) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /", root)
	mux.HandleFunc("GET /hello/{name}", hello)
	mux.HandleFunc("POST /name", generateName)
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, 200, map[string]string{"status": "ok"}) })
	mux.HandleFunc("GET /mail/test", mailTest)
	registerSchoolRoutes(mux, db)
	registerStudentRoutes(mux, db)
	registerStudentCourseRoutes(mux, db)
	registerAuthRoutes(mux, db)
	registerCommerceRoutes(mux, db)
	registerArtRoutes(mux, db)
	registerRegionRoutes(mux, redisClient)
	return cors(requireAdminAuth(mux))
}
func decode(r *http.Request, dst any) error {
	dec := json.NewDecoder(io.LimitReader(r.Body, 1<<20))
	dec.DisallowUnknownFields()
	return dec.Decode(dst)
}
func apiResult(w http.ResponseWriter, data any) {
	writeJSON(w, 200, result{200, "閺屻儴顕楅幋鎰", data})
}
func ok(w http.ResponseWriter)                   { writeJSON(w, 200, result{200, "閹垮秳缍旈幋鎰", nil}) }
func bad(w http.ResponseWriter, msg string)      { writeJSON(w, 400, map[string]string{"detail": msg}) }
func notFound(w http.ResponseWriter, msg string) { writeJSON(w, 404, map[string]string{"detail": msg}) }
func idFrom(r *http.Request, key string) (uint, error) {
	n, e := strconv.ParseUint(r.PathValue(key), 10, 32)
	return uint(n), e
}
func registerSchoolRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /school", func(w http.ResponseWriter, r *http.Request) {
		var x data.School
		if decode(r, &x) != nil || strings.TrimSpace(x.Name) == "" || strings.TrimSpace(x.Address) == "" {
			bad(w, "name and address are required")
			return
		}
		x.CreatedTime = time.Now()
		if e := db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("GET /school", func(w http.ResponseWriter, r *http.Request) {
		var xs []data.School
		if e := db.Order("id").Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		apiResult(w, xs)
	})
	m.HandleFunc("GET /school/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		var x data.School
		if e = db.First(&x, id).Error; e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, x)
	})
	m.HandleFunc("PUT /school/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		var x data.School
		if e = db.First(&x, id).Error; e != nil {
			writeDBError(w, e)
			return
		}
		var in struct {
			Name    *string `json:"name"`
			Address *string `json:"address"`
		}
		if decode(r, &in) != nil {
			bad(w, "invalid JSON")
			return
		}
		if in.Name != nil {
			x.Name = *in.Name
		}
		if in.Address != nil {
			x.Address = *in.Address
		}
		if e = db.Save(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("DELETE /school/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		e = db.Transaction(func(tx *gorm.DB) error {
			var teachers []data.Teacher
			if e := tx.Where("school_id = ?", id).Find(&teachers).Error; e != nil {
				return e
			}
			ids := make([]uint, len(teachers))
			for i, t := range teachers {
				ids[i] = t.ID
			}
			if len(ids) > 0 {
				var students []data.Student
				if e := tx.Where("teacher_id IN ?", ids).Find(&students).Error; e != nil {
					return e
				}
				sids := make([]uint, len(students))
				for i, s := range students {
					sids[i] = s.ID
				}
				if len(sids) > 0 {
					if e := tx.Where("student_id IN ?", sids).Delete(&data.StudentCourse{}).Error; e != nil {
						return e
					}
				}
				if e := tx.Where("teacher_id IN ?", ids).Delete(&data.Student{}).Error; e != nil {
					return e
				}
			}
			if e := tx.Where("school_id = ?", id).Delete(&data.Teacher{}).Error; e != nil {
				return e
			}
			return tx.Delete(&data.School{}, id).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	registerTeacherRoutes(m, db)
	registerCourseRoutes(m, db)
}
func registerTeacherRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /teacher", func(w http.ResponseWriter, r *http.Request) {
		var x data.Teacher
		if decode(r, &x) != nil || x.Name == "" || x.Sex == "" || x.SchoolID == 0 {
			bad(w, "name, sex, and school_id are required")
			return
		}
		x.CreatedTime = time.Now()
		if e := db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("GET /teacher", func(w http.ResponseWriter, r *http.Request) {
		q := db.Order("id")
		if v := r.URL.Query().Get("school_id"); v != "" {
			q = q.Where("school_id = ?", v)
		}
		var xs []data.Teacher
		if e := q.Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		apiResult(w, xs)
	})
	m.HandleFunc("GET /teacher/{id}", func(w http.ResponseWriter, r *http.Request) { genericGet[data.Teacher](w, r, db, "id") })
	m.HandleFunc("PUT /teacher/{id}", func(w http.ResponseWriter, r *http.Request) { genericUpdate[data.Teacher](w, r, db, "id") })
	m.HandleFunc("DELETE /teacher/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		e = db.Transaction(func(tx *gorm.DB) error {
			var s []data.Student
			if e := tx.Select("id").Where("teacher_id = ?", id).Find(&s).Error; e != nil {
				return e
			}
			ids := make([]uint, len(s))
			for i, x := range s {
				ids[i] = x.ID
			}
			if len(ids) > 0 {
				if e := tx.Where("student_id IN ?", ids).Delete(&data.StudentCourse{}).Error; e != nil {
					return e
				}
			}
			if e := tx.Where("teacher_id = ?", id).Delete(&data.Student{}).Error; e != nil {
				return e
			}
			return tx.Delete(&data.Teacher{}, id).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
}
func registerCourseRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /course", func(w http.ResponseWriter, r *http.Request) {
		var x data.Course
		if decode(r, &x) != nil || strings.TrimSpace(x.Name) == "" {
			bad(w, "name and credit are required")
			return
		}
		x.CreatedTime = time.Now()
		if e := db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("GET /course", func(w http.ResponseWriter, r *http.Request) {
		var xs []data.Course
		if e := db.Order("id").Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		apiResult(w, xs)
	})
	m.HandleFunc("GET /course/{id}", func(w http.ResponseWriter, r *http.Request) { genericGet[data.Course](w, r, db, "id") })
	m.HandleFunc("PUT /course/{id}", func(w http.ResponseWriter, r *http.Request) { genericUpdate[data.Course](w, r, db, "id") })
	m.HandleFunc("DELETE /course/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		e = db.Transaction(func(tx *gorm.DB) error {
			if e := tx.Where("course_id = ?", id).Delete(&data.StudentCourse{}).Error; e != nil {
				return e
			}
			return tx.Delete(&data.Course{}, id).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
}
func genericGet[T any](w http.ResponseWriter, r *http.Request, db *gorm.DB, key string) {
	id, e := idFrom(r, key)
	if e != nil {
		bad(w, "invalid id")
		return
	}
	var x T
	if e = db.First(&x, id).Error; e != nil {
		writeDBError(w, e)
		return
	}
	writeJSON(w, 200, x)
}
func genericUpdate[T any](w http.ResponseWriter, r *http.Request, db *gorm.DB, key string) {
	id, e := idFrom(r, key)
	if e != nil {
		bad(w, "invalid id")
		return
	}
	var x T
	if e = db.First(&x, id).Error; e != nil {
		writeDBError(w, e)
		return
	}
	var fields map[string]any
	if decode(r, &fields) != nil {
		bad(w, "invalid JSON")
		return
	}
	if len(fields) == 0 {
		bad(w, "at least one field is required")
		return
	}
	if e = db.Model(&x).Updates(fields).Error; e != nil {
		writeDBError(w, e)
		return
	}
	ok(w)
}
func writeDBError(w http.ResponseWriter, e error) {
	if errors.Is(e, gorm.ErrRecordNotFound) {
		notFound(w, "record not found")
		return
	}
	writeJSON(w, 500, map[string]string{"detail": "database operation failed"})
}
