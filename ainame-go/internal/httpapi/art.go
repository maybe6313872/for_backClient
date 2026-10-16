package httpapi

import (
	"ainame-go/internal/data"
	"encoding/base64"
	"fmt"
	"github.com/xuri/excelize/v2"
	"gorm.io/gorm"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

const maxArtFile = 100 << 20

func registerArtRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /admin/insertArt", func(w http.ResponseWriter, r *http.Request) {
		r.Body = http.MaxBytesReader(w, r.Body, maxArtFile+1<<20)
		if e := r.ParseMultipartForm(maxArtFile); e != nil {
			writeJSON(w, 413, map[string]string{"detail": "upload too large or malformed"})
			return
		}
		f, _, e := r.FormFile("file")
		if e != nil {
			bad(w, "file is required")
			return
		}
		defer f.Close()
		thumb, e := ioReadLimit(f, maxArtFile)
		if e != nil {
			writeJSON(w, 413, map[string]string{"detail": "file exceeds 100 MB"})
			return
		}
		x := data.Art{Username: r.FormValue("username"), Sex: r.FormValue("sex"), Artcontent: r.FormValue("artcontent"), Thumbnail: thumb, CreatedTime: time.Now()}
		if e = db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]string{"result": "success"})
	})
	m.HandleFunc("POST /admin/delArt", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			IDs []uint `json:"id_arr"`
		}
		if decode(r, &in) != nil || len(in.IDs) == 0 {
			bad(w, "id_arr must not be empty")
			return
		}
		res := db.Where("id IN ?", in.IDs).Delete(&data.Art{})
		if res.Error != nil {
			writeDBError(w, res.Error)
			return
		}
		if res.RowsAffected == 0 {
			bad(w, "no article records found")
			return
		}
		writeJSON(w, 200, res.RowsAffected)
	})
	m.HandleFunc("POST /admin/changeArt", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			ID  uint   `json:"id"`
			Sex string `json:"sex"`
		}
		if decode(r, &in) != nil || in.ID == 0 || strings.TrimSpace(in.Sex) == "" {
			bad(w, "id and sex are required")
			return
		}
		res := db.Model(&data.Art{}).Where("id = ?", in.ID).Update("sex", in.Sex)
		if res.Error != nil {
			writeDBError(w, res.Error)
			return
		}
		if res.RowsAffected == 0 {
			notFound(w, "article not found")
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "updated successfully", "data": in.ID})
	})
	m.HandleFunc("POST /admin/queryArt", artQuery(db, false))
	m.HandleFunc("POST /admin/queryArtOut", artQuery(db, true))
	m.HandleFunc("POST /admin/queryArtExcel", artExcel(db))
	m.HandleFunc("POST /admin/insertArtByExcel", artExcelImport(db))
}
func artQuery(db *gorm.DB, wrapped bool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			Page int    `json:"page"`
			Size int    `json:"size"`
			Sex  string `json:"sex"`
		}
		if decode(r, &in) != nil || strings.TrimSpace(in.Sex) == "" {
			bad(w, "sex is required")
			return
		}
		if in.Page < 1 {
			in.Page = 1
		}
		if in.Size < 1 {
			in.Size = 10
		}
		if in.Size > 100 {
			in.Size = 100
		}
		var xs []data.Art
		if e := db.Select("id", "username", "sex", "artcontent").Where("sex = ?", in.Sex).Order("created_time DESC").Offset((in.Page - 1) * in.Size).Limit(in.Size).Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		out := make([]map[string]any, 0, len(xs))
		for _, a := range xs {
			out = append(out, map[string]any{"id": a.ID, "username": a.Username, "sex": a.Sex, "artcontent": a.Artcontent})
		}
		if wrapped {
			writeJSON(w, 200, map[string]any{"code": 200, "message": "查询成功", "data": out})
		} else {
			writeJSON(w, 200, out)
		}
	}
}
func artExcel(db *gorm.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			Page int    `json:"page"`
			Size int    `json:"size"`
			Sex  string `json:"sex"`
		}
		if decode(r, &in) != nil || in.Sex == "" {
			bad(w, "sex is required")
			return
		}
		if in.Page < 1 {
			in.Page = 1
		}
		if in.Size < 1 {
			in.Size = 10
		}
		if in.Size > 100 {
			in.Size = 100
		}
		var xs []data.Art
		if e := db.Select("id", "username", "sex", "artcontent").Where("sex = ?", in.Sex).Order("created_time DESC").Offset((in.Page - 1) * in.Size).Limit(in.Size).Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		f := excelize.NewFile()
		defer f.Close()
		sheet := "文章列表"
		f.SetSheetName("Sheet1", sheet)
		for i, h := range []string{"ID", "用户名", "性别", "文章内容"} {
			cell, _ := excelize.CoordinatesToCellName(i+1, 1)
			_ = f.SetCellValue(sheet, cell, h)
		}
		for ri, a := range xs {
			values := []any{a.ID, a.Username, a.Sex, a.Artcontent}
			for ci, v := range values {
				cell, _ := excelize.CoordinatesToCellName(ci+1, ri+2)
				_ = f.SetCellValue(sheet, cell, v)
			}
		}
		blob, e := f.WriteToBuffer()
		if e != nil {
			writeJSON(w, 500, map[string]string{"detail": "could not generate spreadsheet"})
			return
		}
		stamp := time.Now().Format("20060102_150405")
		filename := "article_list_" + stamp + ".xlsx"
		w.Header().Set("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
		w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=\"%s\"; filename*=UTF-8''%s", filename, url.QueryEscape("文章列表_"+stamp+".xlsx")))
		w.WriteHeader(200)
		_, _ = w.Write(blob.Bytes())
	}
}
func artExcelImport(db *gorm.DB) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		r.Body = http.MaxBytesReader(w, r.Body, maxArtFile)
		if e := r.ParseMultipartForm(8 << 20); e != nil {
			writeJSON(w, 413, map[string]string{"detail": "upload too large or malformed"})
			return
		}
		f, header, e := r.FormFile("file")
		if e != nil {
			bad(w, "file is required")
			return
		}
		defer f.Close()
		if !strings.EqualFold(header.Filename[strings.LastIndex(header.Filename, ".")+1:], "xlsx") {
			bad(w, "only .xlsx is currently supported")
			return
		}
		book, e := excelize.OpenReader(f)
		if e != nil {
			bad(w, "invalid Excel workbook")
			return
		}
		defer book.Close()
		sheets := book.GetSheetList()
		if len(sheets) == 0 {
			bad(w, "workbook is empty")
			return
		}
		rows, e := book.GetRows(sheets[0])
		if e != nil || len(rows) < 2 {
			bad(w, "workbook has no data rows")
			return
		}
		headers := rows[0]
		col := func(names ...string) int {
			for i, h := range headers {
				for _, n := range names {
					if strings.EqualFold(strings.TrimSpace(h), n) {
						return i
					}
				}
			}
			return -1
		}
		u := col("用户名", "username", "用户")
		sx := col("性别", "sex")
		c := col("文章内容", "artcontent", "内容", "content")
		th := col("缩略图", "thumbnail", "图片", "image")
		if u < 0 || sx < 0 || c < 0 {
			bad(w, "required columns: username, sex, artcontent")
			return
		}
		created := 0
		e = db.Transaction(func(tx *gorm.DB) error {
			for _, row := range rows[1:] {
				value := func(i int) string {
					if i < 0 || i >= len(row) {
						return ""
					}
					return strings.TrimSpace(row[i])
				}
				username, sex, content := value(u), value(sx), value(c)
				if username == "" || sex == "" || content == "" || len(username) > 100 || len(sex) > 10 || len(content) > 5000 {
					continue
				}
				var image []byte
				if value(th) != "" {
					image, _ = base64.StdEncoding.DecodeString(value(th))
				}
				if e := tx.Create(&data.Art{Username: username, Sex: sex, Artcontent: content, Thumbnail: image, CreatedTime: time.Now()}).Error; e != nil {
					return e
				}
				created++
			}
			return nil
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		if created == 0 {
			bad(w, "no valid article rows in workbook")
			return
		}
		writeJSON(w, 200, map[string]string{"result": "success"})
	}
}
func ioReadLimit(r interface{ Read([]byte) (int, error) }, max int64) ([]byte, error) {
	b := make([]byte, 0)
	buf := make([]byte, 32*1024)
	for {
		n, e := r.Read(buf)
		if n > 0 {
			if int64(len(b)+n) > max {
				return nil, fmt.Errorf("file too large")
			}
			b = append(b, buf[:n]...)
		}
		if e != nil {
			if e.Error() == "EOF" {
				break
			}
			return nil, e
		}
	}
	return b, nil
}

var _ = strconv.Itoa
