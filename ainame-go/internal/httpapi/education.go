package httpapi

import (
	"ainame-go/internal/data"
	"gorm.io/gorm"
	"net/http"
	"strconv"
	"time"
)

type courseWithScore struct {
	Course data.Course `json:"course"`
	Score  *float32    `json:"score"`
}
type studentOut struct {
	data.Student
	Courses []courseWithScore `json:"courses"`
}
type studentCourseRow struct {
	ID          uint      `json:"id"`
	StudentID   uint      `json:"student_id"`
	CourseID    uint      `json:"course_id"`
	Score       *float32  `json:"score"`
	CreatedTime time.Time `json:"created_time"`
}
type studentByCourse struct {
	StudentID   uint     `json:"student_id"`
	StudentName string   `json:"student_name"`
	StudentSex  string   `json:"student_sex"`
	StudentAge  int      `json:"student_age"`
	TeacherID   uint     `json:"teacher_id"`
	Score       *float32 `json:"score"`
}

func registerStudentRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /student", func(w http.ResponseWriter, r *http.Request) {
		var x data.Student
		if decode(r, &x) != nil || x.Name == "" || x.Sex == "" || x.TeacherID == 0 {
			bad(w, "name, sex, and teacher_id are required")
			return
		}
		x.CreatedTime = time.Now()
		if e := db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("GET /student", func(w http.ResponseWriter, r *http.Request) {
		q := db.Order("id")
		if v := r.URL.Query().Get("teacher_id"); v != "" {
			q = q.Where("teacher_id = ?", v)
		}
		var xs []data.Student
		if e := q.Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		out := make([]studentOut, 0, len(xs))
		for _, s := range xs {
			o, e := makeStudentOut(db, s)
			if e != nil {
				writeDBError(w, e)
				return
			}
			out = append(out, o)
		}
		apiResult(w, out)
	})
	m.HandleFunc("GET /student/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		var s data.Student
		if e = db.First(&s, id).Error; e != nil {
			writeDBError(w, e)
			return
		}
		o, e := makeStudentOut(db, s)
		if e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, o)
	})
	m.HandleFunc("PUT /student/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		var old data.Student
		if e = db.First(&old, id).Error; e != nil {
			writeDBError(w, e)
			return
		}
		var in struct {
			Name      *string `json:"name"`
			Sex       *string `json:"sex"`
			Age       *int    `json:"age"`
			TeacherID *uint   `json:"teacher_id"`
		}
		if decode(r, &in) != nil {
			bad(w, "invalid JSON")
			return
		}
		if in.Name != nil {
			old.Name = *in.Name
		}
		if in.Sex != nil {
			old.Sex = *in.Sex
		}
		if in.Age != nil {
			old.Age = *in.Age
		}
		if in.TeacherID != nil {
			old.TeacherID = *in.TeacherID
		}
		if e = db.Save(&old).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("DELETE /student/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		e = db.Transaction(func(tx *gorm.DB) error {
			if e := tx.Where("student_id = ?", id).Delete(&data.StudentCourse{}).Error; e != nil {
				return e
			}
			return tx.Delete(&data.Student{}, id).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
}
func makeStudentOut(db *gorm.DB, s data.Student) (studentOut, error) {
	var rows []data.StudentCourse
	if e := db.Where("student_id = ?", s.ID).Order("id").Find(&rows).Error; e != nil {
		return studentOut{}, e
	}
	courses := make([]courseWithScore, 0, len(rows))
	for _, row := range rows {
		var c data.Course
		if e := db.First(&c, row.CourseID).Error; e != nil {
			continue
		}
		courses = append(courses, courseWithScore{c, row.Score})
	}
	return studentOut{s, courses}, nil
}
func registerStudentCourseRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /student-course", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			StudentID uint       `json:"student_id"`
			CourseIDs []uint     `json:"course_ids"`
			Scores    []*float32 `json:"scores"`
		}
		if decode(r, &in) != nil || in.StudentID == 0 || len(in.CourseIDs) == 0 {
			bad(w, "student_id and course_ids are required")
			return
		}
		if len(in.Scores) > 0 && len(in.Scores) != len(in.CourseIDs) {
			bad(w, "scores length must match course_ids")
			return
		}
		e := db.Transaction(func(tx *gorm.DB) error {
			if e := tx.Where("student_id = ?", in.StudentID).Delete(&data.StudentCourse{}).Error; e != nil {
				return e
			}
			for i, cid := range in.CourseIDs {
				var score *float32
				if i < len(in.Scores) {
					score = in.Scores[i]
				}
				row := data.StudentCourse{StudentID: in.StudentID, CourseID: cid, Score: score, CreatedTime: time.Now()}
				if e := tx.Create(&row).Error; e != nil {
					return e
				}
			}
			return nil
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("POST /student-course/single", func(w http.ResponseWriter, r *http.Request) {
		var x data.StudentCourse
		if decode(r, &x) != nil || x.StudentID == 0 || x.CourseID == 0 {
			bad(w, "student_id and course_id are required")
			return
		}
		x.CreatedTime = time.Now()
		if e := db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("GET /student-course", func(w http.ResponseWriter, r *http.Request) {
		q := db.Model(&data.StudentCourse{}).Order("id")
		for _, k := range []string{"student_id", "course_id"} {
			if v := r.URL.Query().Get(k); v != "" {
				q = q.Where(k+" = ?", v)
			}
		}
		var rows []data.StudentCourse
		if e := q.Find(&rows).Error; e != nil {
			writeDBError(w, e)
			return
		}
		out := make([]studentCourseRow, 0, len(rows))
		for _, x := range rows {
			out = append(out, studentCourseRow{x.ID, x.StudentID, x.CourseID, x.Score, x.CreatedTime})
		}
		apiResult(w, out)
	})
	m.HandleFunc("GET /student-course/course/{courseId}/students", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "courseId")
		if e != nil {
			bad(w, "invalid course id")
			return
		}
		var rows []data.StudentCourse
		if e = db.Where("course_id = ?", id).Order("id").Find(&rows).Error; e != nil {
			writeDBError(w, e)
			return
		}
		out := make([]studentByCourse, 0, len(rows))
		for _, row := range rows {
			var s data.Student
			if e = db.First(&s, row.StudentID).Error; e != nil {
				continue
			}
			out = append(out, studentByCourse{s.ID, s.Name, s.Sex, s.Age, s.TeacherID, row.Score})
		}
		apiResult(w, out)
	})
	m.HandleFunc("GET /student-course/{id}", func(w http.ResponseWriter, r *http.Request) { genericGet[data.StudentCourse](w, r, db, "id") })
	m.HandleFunc("PUT /student-course/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := idFrom(r, "id")
		if e != nil {
			bad(w, "invalid id")
			return
		}
		var x data.StudentCourse
		if e = db.First(&x, id).Error; e != nil {
			writeDBError(w, e)
			return
		}
		var in struct {
			Score *float32 `json:"score"`
		}
		if decode(r, &in) != nil {
			bad(w, "invalid JSON")
			return
		}
		if in.Score == nil {
			bad(w, "score is required")
			return
		}
		x.Score = in.Score
		if e = db.Save(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
	m.HandleFunc("DELETE /student-course/{id}", func(w http.ResponseWriter, r *http.Request) {
		id, e := strconv.ParseUint(r.PathValue("id"), 10, 32)
		if e != nil {
			bad(w, "invalid id")
			return
		}
		if e = db.Delete(&data.StudentCourse{}, uint(id)).Error; e != nil {
			writeDBError(w, e)
			return
		}
		ok(w)
	})
}
