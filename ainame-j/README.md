# 知了 AI 起名 - Java 后端

`ainame-j` 是 `.net-ainame` 的 Java/Spring Boot 重构版，目标是保持原 FastAPI/.NET 版本的核心路由和 JSON 风格，同时使用 Java 后端主流技术栈。

## 技术栈

| 技术 | 用处 | 本项目里负责什么 |
|---|---|---|
| Java 21 | 后端开发语言和运行平台 | 编写 Controller、Service、Entity、Repository 等所有业务代码；Java 21 是成熟稳定的 LTS 版本，生态兼容性好，很适合学习和企业后端项目。 |
| Spring Boot 3.5.x | Java 后端应用脚手架和自动配置框架 | 自动启动 Web 服务、加载配置、扫描组件、装配依赖，减少大量手写配置。 |
| Spring Web MVC | HTTP 接口框架 | 实现 `/auth/login`、`/school`、`/order/query` 等 REST API；对应 .NET 版的 Controllers。 |
| Spring Data JPA / Hibernate | ORM 数据访问框架 | 用 Java Entity 映射 MySQL 表，用 Repository 操作数据库；对应 .NET 版的 EF Core。 |
| Spring Security + JWT | 认证与接口保护 | 登录后签发 JWT；访问 `/admin/queryArt` 时校验 `Authorization: Bearer ...`。 |
| MySQL Connector/J | MySQL 数据库驱动 | 让 Java 应用能连接 `zhiliao_ainame` 数据库并执行 SQL。 |
| Spring Data Redis | Redis 客户端与数据访问封装 | 支撑 `/region/*` 省市区接口，把省/市/区示例数据写入 Redis 并读取。 |
| Spring Mail | 邮件发送封装 | 支撑 `/auth/code` 验证码邮件和 `/mail/test` 邮件测试。 |
| Apache POI | Office/Excel 文件读写库 | 实现 `/admin/queryArtExcel` 导出 Excel 和 `/admin/insertArtByExcel` 导入 Excel。 |
| springdoc OpenAPI / Swagger UI | API 文档和在线调试页面 | 自动生成 OpenAPI 文档，并在 `/docs` 提供 Swagger UI。 |
| Maven | Java 项目构建和依赖管理工具 | 管理第三方依赖、编译、打包、运行；对应 Node 里的 npm/yarn/pnpm 一类工具。 |

简单类比：

```text
Java 21              ≈ TypeScript/JavaScript 语言本身
Maven pom.xml        ≈ package.json
Maven Central        ≈ npmjs.com
Spring Boot          ≈ 后端框架脚手架 + 自动配置
Spring Web MVC       ≈ Express/Fastify/NestJS 的路由层
Spring Data JPA      ≈ ORM，类似 Prisma/TypeORM/SQLAlchemy/EF Core
target/              ≈ dist/build 输出目录
```

## 快速启动

本机需要先安装：

- JDK 21
- Maven 3.9+
- MySQL，数据库名默认 `zhiliao_ainame`
- Redis，可选；只测 `/region/*` 时需要

在 `ainame-j` 根目录执行：

```powershell
mvn clean package
mvn spring-boot:run
```

默认地址：

```text
http://localhost:5028/
http://localhost:5028/docs
```

配置文件：

```text
src/main/resources/application.yml
src/main/resources/application-dev.yml
```

开发环境默认 MySQL 密码在 `application-dev.yml` 中配置为 `root`，请按你的本地环境修改。

更多说明见：

- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)
- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
- [docs/JS_TO_JAVA_SPRING.md](docs/JS_TO_JAVA_SPRING.md)
- [docs/FRONTEND_TO_JAVA_ROADMAP.md](docs/FRONTEND_TO_JAVA_ROADMAP.md)
