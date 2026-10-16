package httpapi

import (
	"ainame-go/internal/data"
	"gorm.io/gorm"
	"net/http"
	"strings"
	"time"
)

func registerCommerceRoutes(m *http.ServeMux, db *gorm.DB) {
	m.HandleFunc("POST /company/create", func(w http.ResponseWriter, r *http.Request) {
		var x data.Company
		if decode(r, &x) != nil || strings.TrimSpace(x.Name) == "" || x.Address == "" {
			bad(w, "name and address are required")
			return
		}
		x.CreatedTime = time.Now()
		if e := db.Create(&x).Error; e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "created successfully", "data": 1})
	})
	m.HandleFunc("GET /company/query", func(w http.ResponseWriter, r *http.Request) {
		var xs []data.Company
		if e := db.Order("id").Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		if len(xs) == 0 {
			notFound(w, "company not found")
			return
		}
		apiResult(w, xs)
	})
	m.HandleFunc("PUT /company/update", func(w http.ResponseWriter, r *http.Request) {
		var in data.Company
		if decode(r, &in) != nil || in.ID == 0 {
			bad(w, "id, name and address are required")
			return
		}
		if e := db.Model(&data.Company{}).Where("id = ?", in.ID).Updates(map[string]any{"name": in.Name, "address": in.Address}).Error; e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "updated successfully", "data": 1})
	})
	m.HandleFunc("DELETE /company/delete", func(w http.ResponseWriter, r *http.Request) {
		id := r.URL.Query().Get("company_id")
		e := db.Transaction(func(tx *gorm.DB) error {
			var orders []data.Order
			if e := tx.Where("company_id = ?", id).Find(&orders).Error; e != nil {
				return e
			}
			ids := make([]uint, len(orders))
			for i, o := range orders {
				ids[i] = o.ID
			}
			if len(ids) > 0 {
				if e := tx.Where("order_id IN ?", ids).Delete(&data.OrderProduct{}).Error; e != nil {
					return e
				}
			}
			if e := tx.Where("company_id = ?", id).Delete(&data.Order{}).Error; e != nil {
				return e
			}
			return tx.Where("id = ?", id).Delete(&data.Company{}).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "deleted successfully", "data": 1})
	})
	m.HandleFunc("POST /product/create", productWrite(db, false))
	m.HandleFunc("PUT /product/update", productWrite(db, true))
	m.HandleFunc("GET /product/query", func(w http.ResponseWriter, r *http.Request) {
		var xs []data.Product
		if e := db.Order("id").Find(&xs).Error; e != nil {
			writeDBError(w, e)
			return
		}
		apiResult(w, xs)
	})
	m.HandleFunc("DELETE /product/delete", func(w http.ResponseWriter, r *http.Request) {
		id := r.URL.Query().Get("prduct_id")
		e := db.Transaction(func(tx *gorm.DB) error {
			var lines []data.OrderProduct
			if e := tx.Where("product_id = ?", id).Find(&lines).Error; e != nil {
				return e
			}
			ids := map[uint]bool{}
			for _, l := range lines {
				ids[l.OrderID] = true
			}
			for oid := range ids {
				if e := tx.Where("order_id = ?", oid).Delete(&data.OrderProduct{}).Error; e != nil {
					return e
				}
			}
			if e := tx.Where("product_id = ?", id).Delete(&data.OrderProduct{}).Error; e != nil {
				return e
			}
			return tx.Where("id = ?", id).Delete(&data.Product{}).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "deleted successfully", "data": 1})
	})
	m.HandleFunc("POST /order/create", orderWrite(db, false))
	m.HandleFunc("PUT /order/update", orderWrite(db, true))
	m.HandleFunc("GET /order/query", func(w http.ResponseWriter, r *http.Request) {
		var orders []data.Order
		if e := db.Order("id").Find(&orders).Error; e != nil {
			writeDBError(w, e)
			return
		}
		out := make([]map[string]any, 0, len(orders))
		for _, o := range orders {
			var company data.Company
			_ = db.First(&company, o.CompanyID).Error
			var lines []data.OrderProduct
			_ = db.Where("order_id = ?", o.ID).Find(&lines).Error
			items := make([]map[string]any, 0, len(lines))
			total := float32(0)
			for _, line := range lines {
				var p data.Product
				_ = db.First(&p, line.ProductID).Error
				total += p.Price * line.Number
				items = append(items, map[string]any{"product_id": line.ProductID, "product_name": nullable(p.Name), "number": line.Number, "price": p.Price})
			}
			out = append(out, map[string]any{"id": o.ID, "order_number": o.OrderNumber, "company_id": o.CompanyID, "company_name": nullable(company.Name), "product_list": items, "total_price": total})
		}
		writeJSON(w, 200, map[string]any{"code": 200, "data": out, "msg": "success"})
	})
	m.HandleFunc("DELETE /order/delete", func(w http.ResponseWriter, r *http.Request) {
		id := r.URL.Query().Get("id")
		e := db.Transaction(func(tx *gorm.DB) error {
			if e := tx.Where("order_id = ?", id).Delete(&data.OrderProduct{}).Error; e != nil {
				return e
			}
			return tx.Where("id = ?", id).Delete(&data.Order{}).Error
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "deleted successfully", "data": 1})
	})
}
func productWrite(db *gorm.DB, update bool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			ID          uint    `json:"id"`
			Name        string  `json:"name"`
			Price       float32 `json:"price"`
			StoreNum    int     `json:"storenum"`
			Description string  `json:"description"`
			ProductNo   string  `json:"productno"`
		}
		if decode(r, &in) != nil || in.Name == "" || in.Description == "" || in.ProductNo == "" {
			bad(w, "all product fields are required")
			return
		}
		p := data.Product{ID: in.ID, Name: in.Name, Price: in.Price, Storenum: in.StoreNum, Description: in.Description, Productno: in.ProductNo}
		if update {
			if p.ID == 0 {
				bad(w, "id is required")
				return
			}
			if e := db.Model(&p).Select("name", "price", "storenum", "description", "productno").Updates(&p).Error; e != nil {
				writeDBError(w, e)
				return
			}
		} else {
			p.CreatedTime = time.Now()
			if e := db.Create(&p).Error; e != nil {
				writeDBError(w, e)
				return
			}
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "success", "data": 1})
	}
}

type orderInput struct {
	ID          uint   `json:"id"`
	OrderNumber string `json:"order_number"`
	CompanyID   uint   `json:"company_id"`
	ProductList []struct {
		ID     uint    `json:"id"`
		Number float32 `json:"number"`
	} `json:"product_list"`
}

func orderWrite(db *gorm.DB, update bool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var in orderInput
		if decode(r, &in) != nil || in.OrderNumber == "" || in.CompanyID == 0 || len(in.ProductList) == 0 {
			bad(w, "order_number, company_id and product_list are required")
			return
		}
		if update && in.ID == 0 {
			bad(w, "id is required")
			return
		}
		e := db.Transaction(func(tx *gorm.DB) error {
			o := data.Order{ID: in.ID, OrderNumber: in.OrderNumber, CompanyID: in.CompanyID}
			if update {
				if e := tx.Model(&o).Updates(map[string]any{"order_number": o.OrderNumber, "company_id": o.CompanyID}).Error; e != nil {
					return e
				}
				if e := tx.Where("order_id = ?", in.ID).Delete(&data.OrderProduct{}).Error; e != nil {
					return e
				}
			} else {
				o.CreatedTime = time.Now()
				if e := tx.Create(&o).Error; e != nil {
					return e
				}
			}
			for _, x := range in.ProductList {
				if e := tx.Create(&data.OrderProduct{OrderID: o.ID, ProductID: x.ID, Number: x.Number, CreatedTime: time.Now()}).Error; e != nil {
					return e
				}
			}
			return nil
		})
		if e != nil {
			writeDBError(w, e)
			return
		}
		writeJSON(w, 200, map[string]any{"code": 200, "message": "success", "data": 1})
	}
}
func nullable(s string) any {
	if s == "" {
		return nil
	}
	return s
}
