package data

import "time"

type User struct {
	ID           uint   `json:"id" gorm:"primaryKey"`
	Email        string `json:"email"`
	Username     string `json:"username"`
	PasswordHash string `json:"-" gorm:"column:password_hash"`
}

func (User) TableName() string { return "user" }

type EmailCode struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Email       string    `json:"email"`
	Code        string    `json:"code"`
	CreatedTime time.Time `json:"created_time"`
	Type        string    `json:"type"`
}

func (EmailCode) TableName() string { return "email_code" }

type Art struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Username    string    `json:"username"`
	Sex         string    `json:"sex"`
	Artcontent  string    `json:"artcontent" gorm:"column:artcontent"`
	Thumbnail   []byte    `json:"thumbnail"`
	CreatedTime time.Time `json:"created_time"`
}

func (Art) TableName() string { return "art" }

type School struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Name        string    `json:"name"`
	Address     string    `json:"address"`
	CreatedTime time.Time `json:"created_time"`
}

func (School) TableName() string { return "school" }

type Teacher struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Name        string    `json:"name"`
	Sex         string    `json:"sex"`
	Age         int       `json:"age"`
	SchoolID    uint      `json:"school_id"`
	CreatedTime time.Time `json:"created_time"`
}

func (Teacher) TableName() string { return "teacher" }

type Student struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Name        string    `json:"name"`
	Sex         string    `json:"sex"`
	Age         int       `json:"age"`
	TeacherID   uint      `json:"teacher_id"`
	CreatedTime time.Time `json:"created_time"`
}

func (Student) TableName() string { return "student" }

type Course struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Name        string    `json:"name"`
	Credit      float32   `json:"credit"`
	CreatedTime time.Time `json:"created_time"`
}

func (Course) TableName() string { return "course" }

type StudentCourse struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	StudentID   uint      `json:"student_id"`
	CourseID    uint      `json:"course_id"`
	Score       *float32  `json:"score"`
	CreatedTime time.Time `json:"created_time"`
}

func (StudentCourse) TableName() string { return "student_course" }

type Company struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Name        string    `json:"name"`
	Address     string    `json:"address"`
	CreatedTime time.Time `json:"created_time"`
}

func (Company) TableName() string { return "company" }

type Product struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Name        string    `json:"name"`
	Price       float32   `json:"price"`
	Storenum    int       `json:"storenum" gorm:"column:storenum"`
	Description string    `json:"description"`
	Productno   string    `json:"productno" gorm:"column:productno"`
	CreatedTime time.Time `json:"created_time"`
}

func (Product) TableName() string { return "product" }

type Order struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	OrderNumber string    `json:"order_number"`
	CompanyID   uint      `json:"company_id"`
	CreatedTime time.Time `json:"created_time"`
}

func (Order) TableName() string { return "order" }

type OrderProduct struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	OrderID     uint      `json:"order_id"`
	ProductID   uint      `json:"product_id"`
	Number      float32   `json:"number"`
	CreatedTime time.Time `json:"created_time"`
}

func (OrderProduct) TableName() string { return "order_product" }
