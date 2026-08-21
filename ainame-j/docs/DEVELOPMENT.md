# ainame-j 开发指南

本文说明 Java/Spring Boot 重构版如何启动、如何理解技术栈、如何与 `.net-ainame` 对照学习。

## 1. 项目定位

`ainame-j` 是对 `.net-ainame` 的 Java 重构，保留主要业务模块：

- 根路径、邮件测试
- 注册、登录、JWT
- 起名 mock 接口
- 文章 CRUD、Excel 导入导出
- 省市区 Redis
- 学校、班主任、学生、课程、选课
- 公司、产品、订单

默认端口使用 `5028`，避免和 .NET 版 `5027` 冲突。

## 2. 技术栈说明

| 能力 | Java 版 | .NET 版对照 |
|---|---|---|
| Web 框架 | Spring Boot + Spring Web MVC | ASP.NET Core MVC |
| 数据访问 | Spring Data JPA + Hibernate | EF Core |
| 数据库 | MySQL Connector/J | Pomelo.EntityFrameworkCore.MySql |
| 认证 | Spring Security + JWT | JwtBearer |
| 邮件 | Spring Mail | MailKit |
| Redis | Spring Data Redis | StackExchange.Redis |
| Excel | Apache POI | ClosedXML |
| Swagger | springdoc OpenAPI | Swashbuckle |
| 包管理 | Maven | NuGet / `.csproj` |

## 3. 启动前准备

确认命令可用：

```powershell
java -version
mvn -version
```

推荐版本：

```text
Java 21
Maven 3.9+
```

启动 MySQL，并准备数据库：

```sql
CREATE DATABASE IF NOT EXISTS zhiliao_ainame CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

如果你已经使用 Python 或 .NET 版本建过表，Java 版可直接指向同一个库。

## 4. 修改本地配置

默认配置在：

```text
src/main/resources/application.yml
src/main/resources/application-dev.yml
```

开发环境默认：

```yaml
server:
  port: 5028

spring:
  datasource:
    url: jdbc:mysql://127.0.0.1:3306/zhiliao_ainame
    username: root
    password: root
```

如你的 MySQL 密码不是 `root`，修改 `application-dev.yml`。

邮件功能需要配置：

```yaml
spring:
  mail:
    username: 你的邮箱
    password: SMTP授权码
```

JWT 开发密钥：

```yaml
app:
  jwt:
    secret-key: dev-only-change-me-please-use-32chars!!
```

生产环境不要使用示例密钥。

## 5. 编译和运行

在 `ainame-j` 根目录：

```powershell
mvn clean package
mvn spring-boot:run
```

访问：

```text
http://localhost:5028/
http://localhost:5028/docs
```

## 6. 数据库表结构

当前 Java 版配置为：

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: none
```

也就是说：**应用启动时不会自动创建或修改表结构**。

这是为了避免误改已有的 Python/.NET 数据库。后续如果要让 Java 版正式管理表结构，建议引入 Flyway 或 Liquibase，把数据库变更写成版本化 SQL。

## 7. 主要路由

### 通用

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 健康检查 |
| GET | `/hello/{name}` | 问候 |
| GET | `/mail/test?email=` | 邮件测试 |

### 认证 / 起名

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/auth/code?email=` | 邮箱验证码 |
| POST | `/auth/register` | 注册 |
| POST | `/auth/login` | 登录 |
| POST | `/name` | 起名 mock |

### 文章

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/admin/insertArt` | multipart 上传文章 |
| POST | `/admin/delArt` | 批量删除 |
| POST | `/admin/changeArt` | 修改文章性别 |
| POST | `/admin/queryArt` | 查询文章，需要 JWT |
| POST | `/admin/queryArtOut` | 包装层查询 |
| POST | `/admin/queryArtExcel` | 导出 Excel |
| POST | `/admin/insertArtByExcel` | 导入 Excel |

### 省市区

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/region/provinces` | 省份 |
| GET | `/region/cities?province_code=` | 城市 |
| GET | `/region/districts?city_code=` | 区县 |
| POST | `/region/init` | 初始化示例数据 |

### 校园

| 前缀 | 说明 |
|---|---|
| `/school` | 学校 CRUD |
| `/teacher` | 班主任 CRUD |
| `/student` | 学生 CRUD |
| `/course` | 课程 CRUD |
| `/student-course` | 学生选课 |

### 订单

| 前缀 | 说明 |
|---|---|
| `/company/*` | 公司 |
| `/product/*` | 产品 |
| `/order/*` | 订单 |

## 8. 学习阅读顺序

建议这样看：

1. `pom.xml`
2. `src/main/resources/application.yml`
3. `AinameJavaApplication.java`
4. `config/SecurityConfig.java`
5. `controller/RootController.java`
6. `controller/AuthController.java`
7. `entity/AppUser.java`
8. `repository/AppUserRepository.java`
9. `service/JwtTokenService.java`

这条线能串起 Spring Boot 后端的主干：启动、配置、Controller、DTO、Entity、Repository、Service、安全认证。
