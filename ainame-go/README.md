# 知了 AI 起名 — Go 后端学习版

这是 `ainame-j`（Java/Spring Boot）的 Go 重写起点，独立写入本目录，不修改 Java 源项目。当前采用 Go 标准库 `net/http`，不依赖 Web 框架；已实现根路由、问候、健康检查和起名 mock 接口。**这不是完整功能等价迁移**：原项目中的 MySQL CRUD、JWT 注册登录、邮件、Redis 行政区、Excel 导入导出及校园/订单模块尚未移植，详见 [迁移状态](docs/MIGRATION_STATUS.md)。

## 运行

安装 Go 1.22 或更新版本后，在本目录执行：

```powershell
go run ./cmd/ainame
# 默认监听 :5029；也可设置 PORT=8080
```

检查：`GET http://localhost:5029/health`。测试：`go test ./...`。项目当前只用标准库，无需下载第三方模块。

## 请求示例

```http
POST /name
Content-Type: application/json

{"surname":"张","gender":"不限","length":"两字","other":"温柔","exclude":[]}
```

## 文档导航

- [学习导览：从请求到响应](docs/LEARNING_GUIDE.md)
- [Java 到 Go 概念映射](docs/JAVA_TO_GO.md)
- [原项目功能与迁移状态](docs/MIGRATION_STATUS.md)
- [源项目结构摘要](docs/ARCHITECTURE.md)

## 安全配置提醒

原 Java `application.yml` 含 SMTP 凭证样式的明文值。不要把它复制到 Go 仓库；若凭证真实且曾提交到 Git，应立即轮换，并改用环境变量或密钥管理服务。当前 Go 版本不发送邮件，也不处理任何凭证。
