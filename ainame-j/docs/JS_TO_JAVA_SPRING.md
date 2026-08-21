# JS 到 Java/Spring Boot 对照

本文给有 JavaScript/前端经验的开发者看，用熟悉的概念理解 Java 后端。

## 1. 项目与依赖

| JS / Node | Java / Spring Boot |
|---|---|
| `package.json` | `pom.xml` |
| npm | Maven |
| npmjs.com | Maven Central |
| `npm install` | `mvn dependency:resolve` 或 `mvn package` 自动下载依赖 |
| `npm run dev` | `mvn spring-boot:run` |
| `node_modules` | 本机 Maven 仓库 `~/.m2/repository` + `target/` |
| `dist/` | `target/` |

## 2. import

JS：

```js
import express from "express";
```

Java：

```java
import org.springframework.web.bind.annotation.RestController;
```

Java 的 `import` 是导入类的完整包名。真正让项目拥有第三方库的是 `pom.xml` 里的 dependency。

## 3. package

Java 文件顶部常见：

```java
package com.zhiliao.ainame.controller;
```

这类似 C# 的 namespace，也有点像 JS 项目里的目录分组，但它是 Java 类型系统的一部分。

目录通常和 package 对齐：

```text
src/main/java/com/zhiliao/ainame/controller/AuthController.java
```

对应：

```java
package com.zhiliao.ainame.controller;
```

## 4. Controller

Express：

```js
app.post("/auth/login", async (req, res) => {});
```

Spring Boot：

```java
@RestController
@RequestMapping("/auth")
public class AuthController {
    @PostMapping("/login")
    public LoginResponse login(@RequestBody LoginRequest data) {
        return result;
    }
}
```

组合后就是：

```text
POST /auth/login
```

## 5. DTO

TypeScript：

```ts
type LoginRequest = {
  email: string;
  password: string;
};
```

Java record：

```java
public record LoginRequest(String email, String password) {
}
```

`record` 很适合做请求/响应模型。

## 6. Entity / Repository

前端通常只接触接口数据；后端还要管理数据库表。

Entity：

```java
@Entity
@Table(name = "`user`")
public class AppUser {
    @Id
    private Integer id;
}
```

Repository：

```java
public interface AppUserRepository extends JpaRepository<AppUser, Integer> {
    Optional<AppUser> findByEmail(String email);
}
```

Spring Data JPA 会根据方法名自动生成查询。

## 7. 依赖注入

JS 中常见：

```js
const authController = new AuthController(userRepo, jwtService);
```

Spring 中通常不手动 new：

```java
public AuthController(AppUserRepository users, JwtTokenService jwtTokenService) {
    this.users = users;
    this.jwtTokenService = jwtTokenService;
}
```

只要 `AppUserRepository`、`JwtTokenService` 被 Spring 管理，框架会自动注入。

常见注解：

| 注解 | 作用 |
|---|---|
| `@RestController` | HTTP Controller |
| `@Service` | 业务服务 |
| `@Repository` | 数据访问组件，Spring Data JPA 接口通常不用手写 |
| `@Configuration` | 配置类 |
| `@Bean` | 把方法返回值注册进 Spring 容器 |

## 8. async/await 与 Java

Spring MVC 默认是同步线程模型。代码里通常直接写：

```java
var user = users.findByEmail(email).orElse(null);
```

不像 Node/JS 那样每个 IO 都显式 `await`。Spring Boot 会为每个 HTTP 请求分配线程，数据库连接由连接池管理。

## 9. JSON snake_case

项目配置：

```yaml
spring:
  jackson:
    property-naming-strategy: SNAKE_CASE
```

所以 Java 里的：

```java
confirmPassword
```

会对应 JSON：

```json
{
  "confirm_password": "123456"
}
```

这和原 Python/FastAPI、.NET 版的 JSON 风格保持一致。
