# 学习导览：一次 HTTP 请求如何穿过 Go 服务

## 1. 入口与依赖

`cmd/ainame/main.go` 是可执行程序入口：读取端口、创建 `http.Server`、把 `internal/httpapi.New()` 返回的处理器交给服务器。Go 的 `main` 包对应“程序入口”，而不是 Java 中由 Spring 扫描并实例化的启动类。端口通过 `PORT` 环境变量设置，缺省为 5029。

## 2. 路由与 Handler

`internal/httpapi/http.go` 中 `New` 创建 `http.ServeMux` 并注册路由。每个 handler 的签名是 `func(http.ResponseWriter, *http.Request)`：前者写状态码和响应，后者提供方法、路径参数、请求体和上下文。Go 1.22 的 ServeMux 支持 `GET /hello/{name}`，路径变量用 `r.PathValue("name")` 获取。

这相当于 Spring MVC 的 `@GetMapping` + Controller 方法，但 Go 标准库不会自动扫描注解、注入 Service 或序列化 DTO；这些步骤显式写出来，初学者能看清控制流。

## 3. JSON 解码、校验与响应

`NameRequest` 的字段标签（例如 ``json:"surname"``）定义 JSON 名称。`json.Decoder` 将请求体解码为结构体；代码限制请求体大小，并拒绝未知字段。校验失败显式返回 400。`writeJSON` 统一设置 Content-Type、状态码并编码响应。

生产代码通常会将 handler 拆分为 handler/service/repository：handler 只解析协议，service 承载业务规则，repository 负责持久化。当前示例刻意保持小型，尚无数据库层。

## 4. 中间件

`cors(next)` 接收一个 `http.Handler` 并返回另一个 `http.Handler`，这是 Go 常见的装饰器式中间件：请求先经过 CORS，再进入路由。CORS 当前为便于本地学习设为 `*`，上线前必须限制可信前端来源；它不是身份认证。

## 5. 错误处理与并发

Go 通常通过返回 `error` 值表达可恢复错误，而不是抛异常。HTTP 边界将错误映射为 4xx/5xx JSON。`net/http` 会为并发请求提供服务，因此共享状态必须使用同步原语或数据库事务；本示例没有可变全局业务状态。

## 6. 测试

`http_test.go` 使用 `httptest.NewRequest` 和 `httptest.NewRecorder`，不必启动真实端口即可测试 handler。这类似 Spring MockMvc 的思路。建议继续补全：合法起名请求、错误 JSON、方法不允许、超大请求体，以及每个业务服务的单元测试。

## 练习顺序

1. 增加统一错误结构和 request-id middleware。
2. 把 mock 起名逻辑移至 `internal/name`，编写表驱动测试。
3. 接入配置结构和结构化日志。
4. 设计 SQL schema 与 repository，再迁移一个 CRUD 模块。
5. 最后实现 JWT、邮件、Redis 和 Excel；这些集成应有独立接口及可替换的测试实现。
