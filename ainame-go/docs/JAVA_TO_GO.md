# Java / Spring 到 Go 标准库映射

| 原项目概念 | Go 对应做法 | 本仓库示例 |
|---|---|---|
| Maven `pom.xml` | `go.mod` 管理模块和依赖 | `go.mod`（目前无外部依赖） |
| `@RestController` | `http.Handler` / handler 函数 | `internal/httpapi/http.go` |
| `@GetMapping` / `@PostMapping` | `ServeMux.HandleFunc("METHOD /path", ...)` | `New` |
| DTO / Java record | struct + `json` tags | `NameRequest`, `NameItem` |
| Jackson | `encoding/json` | `json.Decoder`、`json.Encoder` |
| Bean Validation | 显式校验或验证库 | `generateName` 中的基础校验 |
| `ResponseEntity` | `WriteHeader` + 写响应体 | `writeJSON` |
| Spring Filter / interceptor | `http.Handler` 包装（middleware） | `cors` |
| Spring Boot 启动与依赖注入 | `main` 显式组装对象 | `cmd/ainame/main.go` |
| JUnit / MockMvc | `testing` + `net/http/httptest` | `http_test.go` |
| JPA/MyBatis repository | 显式 repository 接口 + SQL/ORM | 尚未实现 |

Go 没有强制采用 Controller-Service-Repository 的框架模板。包按职责组织，依赖关系由构造函数/参数显式传递。不要把 Java 的类层级机械翻译成 Go；优先使用小接口、组合和清楚的数据流。

## 可选后续技术

持久化可比较 `database/sql`（标准接口，需驱动）与 GORM；路由可先用标准库，确有需要再评估 Gin/Chi；密码哈希应采用经过审查的 bcrypt/Argon2 实现，JWT、Redis、邮件和 Excel 也应选成熟库。引入依赖前记录版本、许可证、维护状态与安全更新策略。当前仓库刻意不预先锁定这些依赖。
