# 前端开发者转 Java 后端学习路线

本文面向已经有较丰富 JavaScript / TypeScript / 前端工程经验的开发者。目标不是从零背 Java 语法，而是把已有的工程经验迁移到 Java、Spring Boot、Maven、数据库和后端部署上，并且能直接读懂、修改、扩展 `ainame-j` 项目。

## 0. 学习目标

建议把目标拆成四层：

| 阶段 | 目标 | 你最终应该能做到 |
|---|---|---|
| 入门 | 看懂 Java 文件和项目结构 | 能解释 `package`、`import`、`class`、`interface`、`record`、`annotation` |
| 上手 | 能改 Spring Boot 接口 | 能新增一个 Controller 接口，并调用 Service、Repository |
| 业务 | 能操作数据库和鉴权 | 能写 Entity、Repository、DTO、JWT 登录、分页查询 |
| 工程化 | 能打包、配置、部署和排错 | 能用 Maven 构建 jar，区分本地、测试、生产配置 |

这条路线的核心原则是：少做纯语法刷题，多围绕项目文件读代码、改代码、跑接口。

## 1. 版本选择

当前 `ainame-j` 项目使用：

```text
Java 21
Spring Boot 3.5.x
Maven 3.9.x
MySQL
Redis
```

选择 Java 21 的原因是：它是成熟稳定的 LTS 版本，Spring Boot 3.x 生态里非常常见，教程、生产项目、IDE 和依赖兼容性都很稳。对学习 Java 后端来说，Java 21 已经覆盖了你现阶段需要掌握的核心语言能力。

这个项目主要用于学习 Spring Boot 后端主干，用 Java 21 完全够用，也能减少本机环境安装和依赖兼容问题。后续真正进入生产项目时，再根据公司技术栈统一选择 JDK 版本。

Spring Boot 官方当前主线已经进入 4.x，但 Spring Boot 3.x 仍是非常主流的企业项目形态。你先学 Spring Boot 3.x 更适合看大量现有项目，也更贴合本项目。

## 2. JS 到 Java 的核心对照

| 前端 / Node 经验 | Java / Spring Boot 对应物 | 说明 |
|---|---|---|
| `package.json` | `pom.xml` | 声明项目信息、依赖、构建插件 |
| `npm install` | `mvn dependency:resolve` / `mvn package` | 下载依赖到本机 Maven 仓库 |
| `node_modules` | `~/.m2/repository` + `target/` | Maven 依赖缓存和构建产物 |
| `npm run dev` | `mvn spring-boot:run` | 启动开发服务 |
| `npm run build` | `mvn clean package` | 编译、测试、打包 |
| `dist/` | `target/` | 打包后的输出目录 |
| `import xxx from` | `import 包名.类名` | Java 导入的是类、接口、注解等类型 |
| TS `type/interface` | Java `record/class/interface` | DTO 常用 `record`，实体常用 `class` |
| Express route | Spring Controller | HTTP 路由入口 |
| Middleware | Filter / Interceptor / Security FilterChain | 鉴权、日志、跨域等横切逻辑 |
| Prisma / TypeORM | Spring Data JPA / Hibernate | ORM 和数据库访问 |
| `.env` | `application.yml` / 环境变量 | 配置文件和环境变量结合使用 |
| `try/catch` + error middleware | `@ControllerAdvice` | 全局异常处理 |

## 3. 先理解项目目录

建议先看 `ainame-j` 的这几类文件：

```text
ainame-j/
  pom.xml
  src/main/java/com/zhiliao/ainame/
  src/main/resources/application.yml
  docs/
```

其中 Java 源码主目录是：

```text
src/main/java/com/zhiliao/ainame
```

`src/main/java` 是 Maven 标准源码目录。

`com/zhiliao/ainame` 对应 Java 包名：

```java
package com.zhiliao.ainame;
```

它类似 npm 包名里的命名空间，也类似前端项目里的根模块路径。Spring Boot 启动类在这个包下，默认会扫描它下面的子包：

```text
controller
service
repository
entity
dto
config
```

这些目录的职责：

| 目录 | 用途 | 前端类比 |
|---|---|---|
| `controller` | 接收 HTTP 请求，返回响应 | route/controller |
| `service` | 业务逻辑 | service/use-case |
| `repository` | 数据库访问 | Prisma model client / DAO |
| `entity` | 数据表映射模型 | ORM model |
| `dto` | 请求和响应数据结构 | TypeScript type/interface |
| `config` | Spring、鉴权、Swagger、异常处理配置 | app config / middleware |

## 4. 第一阶段：Java 语言基础

建议时间：5 到 7 天。

重点不是把 Java 全部语法学完，而是先学到能读 Spring Boot 代码。

必须掌握：

| 知识点 | 要理解到什么程度 |
|---|---|
| `class` | 类是 Java 的主要代码组织单位 |
| `public/private/final/static` | 权限、不可变、类级成员 |
| 字段和方法 | 对应对象属性和函数 |
| 构造方法 | 类似 JS class constructor |
| `interface` | 定义能力契约，常用于依赖注入 |
| `extends/implements` | 继承类、实现接口 |
| 泛型 `<T>` | 类似 TS 泛型 |
| 集合 `List/Map/Set` | 类似数组、对象、Set，但类型更严格 |
| `Optional` | 表达“可能没有值”，避免直接 `null` |
| 异常 | `throw`、`try/catch`、运行时异常 |
| `record` | 快速定义不可变数据对象，适合 DTO |
| 注解 `@Xxx` | 给框架看的元数据，Spring 大量使用 |

对前端来说，最容易卡的是这几个点：

```text
Java 文件通常一个 public class 对应一个文件
Java 类型名、文件名、包名强相关
Java 方法参数、返回值必须显式声明类型
Java 的 import 只负责引入名字，不负责安装依赖
```

练习任务：

1. 在 `dto` 目录里看懂任意一个 `record`。
2. 在 `entity` 目录里看懂任意一个实体类。
3. 在 `controller` 目录里找一个 `@GetMapping`，说清楚它对应哪个 HTTP 接口。
4. 写一个简单类，包含字段、构造方法、getter、普通方法。

## 5. 第二阶段：Maven 和依赖管理

建议时间：2 到 3 天。

你需要理解 Maven 解决的是三件事：

```text
依赖下载
代码编译
项目打包
```

重点文件：

```text
ainame-j/pom.xml
```

常用命令：

```powershell
mvn -version
mvn dependency:tree
mvn clean package
mvn spring-boot:run
```

重点概念：

| Maven 概念 | 解释 | JS 类比 |
|---|---|---|
| `groupId` | 组织名 | npm scope |
| `artifactId` | 包名 / 项目名 | package name |
| `version` | 版本号 | npm version |
| `dependency` | 第三方依赖 | dependencies |
| `plugin` | 构建插件 | npm script + build tool plugin |
| `target/` | 构建输出 | dist/build |
| `.m2/repository` | 本机依赖缓存 | 全局 npm cache，不是项目内 node_modules |

练习任务：

1. 运行 `mvn dependency:tree`，看项目实际依赖树。
2. 找到 `spring-boot-starter-web`，理解它为什么能带来 Controller 能力。
3. 找到 `mysql-connector-j`，理解它为什么能让项目连接 MySQL。
4. 运行 `mvn clean package`，确认生成 `target/*.jar`。

## 6. 第三阶段：Spring Boot Web

建议时间：1 到 2 周。

先看启动入口：

```text
src/main/java/com/zhiliao/ainame/AinameJavaApplication.java
```

你要形成这个心智模型：

```text
main 方法启动 Spring Boot
Spring Boot 扫描 com.zhiliao.ainame 下面的组件
Controller 暴露 HTTP 接口
Service 处理业务
Repository 操作数据库
返回对象自动序列化成 JSON
```

重点注解：

| 注解 | 用途 |
|---|---|
| `@SpringBootApplication` | 启动类，开启自动配置和组件扫描 |
| `@RestController` | 声明这是 REST 接口控制器 |
| `@RequestMapping` | 给 Controller 设置公共路由前缀 |
| `@GetMapping` | GET 接口 |
| `@PostMapping` | POST 接口 |
| `@RequestBody` | 从请求 body 读取 JSON |
| `@PathVariable` | 读取 URL 路径参数 |
| `@RequestParam` | 读取 query 参数 |
| `@Valid` | 触发参数校验 |

建议按这个顺序读项目代码：

```text
RootController.java
NameController.java
AuthController.java
SchoolController.java
OrderController.java
```

练习任务：

1. 新增一个 `GET /dev/ping`，返回 `{ "message": "pong" }`。
2. 新增一个 `POST /dev/echo`，把请求 JSON 原样返回。
3. 用 Swagger `/docs` 调接口。
4. 故意传错参数，看全局异常处理如何返回错误。

## 7. 第四阶段：DTO、Entity、Repository

建议时间：1 到 2 周。

这阶段是 Java 后端和前端差异最大的地方。前端主要消费接口数据，后端要负责数据如何进入数据库、如何查出来、如何变成响应。

三类模型要分清：

| 类型 | 用途 | 是否直接对应数据库 |
|---|---|---|
| DTO | 请求和响应数据 | 不一定 |
| Entity | 数据库表映射 | 是 |
| Repository | 数据访问接口 | 不是表，但操作表 |

典型流向：

```text
HTTP JSON
  -> Request DTO
  -> Controller
  -> Service
  -> Repository
  -> Entity
  -> MySQL
```

返回时：

```text
MySQL
  -> Entity
  -> Service 组装
  -> Response DTO
  -> JSON
```

重点注解：

| 注解 | 用途 |
|---|---|
| `@Entity` | 声明实体类 |
| `@Table` | 指定数据库表名 |
| `@Id` | 主键 |
| `@GeneratedValue` | 主键生成策略 |
| `@Column` | 字段和列映射 |
| `@ManyToOne` | 多对一关系 |
| `@OneToMany` | 一对多关系 |
| `@JoinColumn` | 外键列 |

Repository 常见写法：

```java
public interface AppUserRepository extends JpaRepository<AppUser, Integer> {
    Optional<AppUser> findByEmail(String email);
}
```

这里最神奇的是 `findByEmail`。Spring Data JPA 会根据方法名生成查询逻辑。它不是 JS 那种运行时随便拼对象，而是框架根据接口方法约定生成实现。

练习任务：

1. 新建一张简单表，比如 `note`。
2. 写 `Note` Entity。
3. 写 `NoteRepository extends JpaRepository<Note, Integer>`。
4. 写 `NoteController`，提供增删改查接口。
5. 用 Swagger 测通。

## 8. 第五阶段：数据库迁移和表结构管理

建议时间：3 到 5 天。

Java 里可以让 Hibernate 自动建表，但正式项目通常不建议长期依赖：

```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: none
```

本项目目前就是 `none`，意思是 Java 应用只使用已有表结构，不自动改数据库。

正式项目更推荐引入数据库迁移工具：

```text
Flyway
Liquibase
```

它们类似前端/Node 后端里的 migration 工具：

```text
Prisma Migrate
TypeORM migration
Knex migration
Sequelize migration
```

学习重点：

| 能力 | 说明 |
|---|---|
| migration 文件 | 每次表结构修改都写成版本化 SQL |
| 版本记录表 | 工具会记录哪些迁移已经执行 |
| 可追踪 | 团队成员、测试环境、生产环境结构一致 |
| 可回滚策略 | 重要变更要能设计回退方案 |

练习任务：

1. 给项目加 Flyway。
2. 新增 `src/main/resources/db/migration/V1__init.sql`。
3. 把已有核心表结构整理进去。
4. 新增一个字段，写 `V2__add_xxx_column.sql`。
5. 启动项目，确认迁移执行。

## 9. 第六阶段：鉴权、安全和 JWT

建议时间：1 周。

本项目相关文件：

```text
config/SecurityConfig.java
config/JwtAuthenticationFilter.java
service/JwtTokenService.java
controller/AuthController.java
entity/AppUser.java
repository/AppUserRepository.java
```

你需要理解这一条链：

```text
用户登录
  -> 校验邮箱和密码
  -> 生成 JWT
  -> 前端保存 token
  -> 后续请求带 Authorization: Bearer token
  -> 后端 Filter 解析 token
  -> Spring Security 判断是否允许访问
```

前端类比：

```text
Axios interceptor 添加 token
后端 middleware 校验 token
React Router guard 控制页面访问
```

Java 后端真正要掌握的是：

| 概念 | 用途 |
|---|---|
| Authentication | 当前用户是谁 |
| Authorization | 当前用户能不能访问 |
| Filter | 请求进入 Controller 前执行 |
| SecurityFilterChain | 安全规则配置 |
| BCrypt | 密码哈希 |
| JWT claim | token 中携带的用户信息 |

练习任务：

1. 注册一个用户。
2. 登录拿到 JWT。
3. 用 Swagger 或接口工具访问 `/admin/*`。
4. 删除 token 再访问，观察返回。
5. 给某个新接口加登录保护。

## 10. 第七阶段：异常、校验、日志

建议时间：3 到 5 天。

本项目相关文件：

```text
config/GlobalExceptionHandler.java
```

后端接口不能只追求“正常情况能跑”，还要处理：

```text
参数缺失
参数类型错误
业务数据不存在
权限不足
数据库异常
外部服务异常
```

重点注解和类：

| 名称 | 用途 |
|---|---|
| `@ControllerAdvice` | 全局异常处理 |
| `@ExceptionHandler` | 指定异常如何转换成响应 |
| `@Valid` | 触发对象校验 |
| `@NotBlank` | 字符串不能为空 |
| `@NotNull` | 值不能为空 |
| `@Size` | 长度限制 |
| `ResponseEntity` | 精细控制 HTTP 状态码和响应体 |

练习任务：

1. 给登录请求 DTO 增加校验。
2. 邮箱为空时返回统一错误结构。
3. 查询不存在的数据时返回 404。
4. 在 Service 里加必要日志。

## 11. 第八阶段：部署和运行

建议时间：3 到 5 天。

Java 后端通常要编译打包。这个过程类似前端打包：

```text
npm run build
  -> dist/

mvn clean package
  -> target/xxx.jar
```

运行方式：

```powershell
java -jar target/ainame-j-0.1.0-SNAPSHOT.jar
```

常见部署形态：

| 方式 | 说明 |
|---|---|
| 直接运行 jar | 最基础，适合学习和简单服务器 |
| systemd / Windows 服务 | 让应用常驻后台并开机启动 |
| Docker | 更接近现在主流部署 |
| CI/CD | 代码提交后自动构建、测试、发布 |

你需要掌握：

```text
本地配置 application-dev.yml
生产配置 application-prod.yml
环境变量覆盖敏感信息
jar 包运行参数
日志文件位置
MySQL/Redis 地址配置
```

练习任务：

1. `mvn clean package` 生成 jar。
2. 用 `java -jar` 启动。
3. 改端口启动一次。
4. 增加 `application-prod.yml`。
5. 用环境变量配置数据库密码。

## 12. 十周学习计划

这个计划按每天 1 到 2 小时设计。如果时间更多，可以压缩到 6 周；如果工作忙，可以拉长到 12 到 16 周。

| 周数 | 主题 | 主要产出 |
|---|---|---|
| 第 1 周 | Java 基础语法 | 能读懂类、接口、泛型、集合、注解 |
| 第 2 周 | Maven 和项目结构 | 能解释 `pom.xml`、`src/main/java`、`target` |
| 第 3 周 | Spring Boot Controller | 能新增 GET/POST 接口 |
| 第 4 周 | DTO、参数校验、异常处理 | 能写请求/响应模型和统一错误响应 |
| 第 5 周 | JPA Entity 和 Repository | 能对单表做增删改查 |
| 第 6 周 | 复杂查询和关联关系 | 能处理分页、条件查询、一对多/多对一 |
| 第 7 周 | 登录、JWT、Spring Security | 能保护接口并识别当前用户 |
| 第 8 周 | Redis、邮件、Excel | 能使用常见基础设施能力 |
| 第 9 周 | 数据库迁移、配置、日志 | 能管理表结构变更和环境配置 |
| 第 10 周 | 打包、部署、项目复盘 | 能交付一个可运行的 jar 或 Docker 服务 |

## 13. 每周具体安排

### 第 1 周：Java 语言

| 天 | 内容 | 练习 |
|---|---|---|
| Day 1 | JDK、JRE、JVM、编译运行 | 写 `HelloJava` 并运行 |
| Day 2 | class、字段、方法、构造方法 | 写一个 `User` 类 |
| Day 3 | `List`、`Map`、循环、条件 | 写用户列表过滤 |
| Day 4 | interface、implements | 写 `EmailSender` 接口和实现类 |
| Day 5 | 泛型、Optional、异常 | 写一个查用户方法 |
| Day 6 | record、枚举、时间类型 | 写请求/响应 DTO |
| Day 7 | 回看项目源码 | 找 5 个不懂的 Java 写法并整理 |

### 第 2 周：Maven 和 Spring Boot 启动

| 天 | 内容 | 练习 |
|---|---|---|
| Day 1 | `pom.xml` 结构 | 标注每个 dependency 的用途 |
| Day 2 | Maven 生命周期 | 运行 `clean/package/test` |
| Day 3 | Spring Boot 启动类 | 理解 `@SpringBootApplication` |
| Day 4 | 配置文件 | 修改端口、数据库配置 |
| Day 5 | Swagger | 用 `/docs` 调接口 |
| Day 6 | 热启动 | 尝试 `mvn spring-boot:run` |
| Day 7 | 总结 | 写一页 Maven 与 npm 对照 |

### 第 3 到 4 周：接口开发

| 内容 | 练习 |
|---|---|
| Controller 路由 | 新增 `/dev/ping` |
| 请求参数 | 新增 query、path、body 三种参数接口 |
| DTO | 用 record 定义请求和响应 |
| 校验 | 给请求字段加 `@NotBlank` |
| 异常 | 统一返回错误格式 |
| Swagger | 确认接口文档能展示新接口 |

### 第 5 到 6 周：数据库

| 内容 | 练习 |
|---|---|
| Entity | 新增 `Note` 实体 |
| Repository | 新增 `NoteRepository` |
| CRUD | 写增删改查 |
| 分页 | 写分页查询 |
| 条件查询 | 写按标题或状态查询 |
| 关联关系 | 学会 `@ManyToOne`、`@OneToMany` |

### 第 7 周：登录和权限

| 内容 | 练习 |
|---|---|
| 密码哈希 | 理解 BCrypt |
| JWT | 理解 token 生成和解析 |
| Filter | 理解请求进入 Controller 前的处理 |
| SecurityConfig | 看懂哪些接口放行、哪些接口保护 |
| 权限测试 | 无 token、错误 token、正确 token 各测一次 |

### 第 8 到 10 周：工程化

| 内容 | 练习 |
|---|---|
| Redis | 读写一个简单 key |
| 邮件 | 配置 SMTP 并发测试邮件 |
| Excel | 用 Apache POI 导出一份 Excel |
| Flyway | 写一个 migration |
| 打包 | 生成 jar 并运行 |
| 部署 | 准备 Dockerfile 或服务器启动脚本 |

## 14. 用 `ainame-j` 做主线练习

不要另起一个特别简单的 demo 项目太久。可以用极小 demo 理解语法，但真正转后端，要尽早回到这个项目。

推荐改造路线：

1. 看懂 `RootController`，理解最简单接口。
2. 看懂 `NameController`，理解业务接口如何返回数据。
3. 看懂 `AuthController`，理解登录注册。
4. 看懂 `AppUser` 和 `AppUserRepository`，理解用户表。
5. 看懂 `SecurityConfig` 和 `JwtAuthenticationFilter`，理解接口保护。
6. 新增一个 `Note` 模块，完整走 Controller、DTO、Entity、Repository。
7. 给 `Note` 模块加分页、搜索、登录保护。
8. 给 `Note` 表加 migration。
9. 打包成 jar 运行。
10. 写一份接口说明，模拟真实交付。

## 15. 推荐学习顺序

更建议按这个顺序学：

```text
Java 基础
  -> Maven
  -> Spring Boot Controller
  -> DTO / 参数校验 / 异常
  -> JPA / MySQL
  -> Spring Security / JWT
  -> Redis / Mail / Excel
  -> Flyway / 部署 / Docker
```

暂时可以晚点学：

```text
JVM 调优
复杂并发
微服务
消息队列
分布式事务
Spring Cloud
Kubernetes
```

这些不是不重要，而是前期学它们容易分散注意力。先把单体 Spring Boot 后端写顺，收益最大。

## 16. 你应该重点建立的后端思维

前端转后端时，最重要的不是语法，而是职责变化。

| 前端更关注 | 后端更关注 |
|---|---|
| UI 状态 | 数据一致性 |
| 页面交互 | 接口契约 |
| 组件拆分 | 分层架构 |
| 浏览器兼容 | 服务稳定性 |
| 请求成功后的展示 | 请求失败时如何正确返回 |
| 本地状态管理 | 数据库事务 |
| token 存哪里 | token 如何签发、校验、过期 |
| 用户体验 | 安全、日志、审计、性能 |

转 Java 后端时，你要经常问自己：

```text
这个接口参数是否合法？
这个操作要不要事务？
这个数据不存在返回什么状态码？
这个字段能不能被前端伪造？
这个异常会不会泄露内部信息？
这个 SQL 会不会很慢？
这个配置能不能进生产环境？
```

## 17. 验收标准

学完这条路线后，你应该可以做到：

```text
能独立启动 ainame-j
能解释 pom.xml 中主要依赖的用途
能新增一个 REST Controller
能定义请求和响应 DTO
能写 Entity 并映射数据库表
能写 Repository 查询数据库
能处理常见异常和参数校验
能理解 JWT 登录流程
能用 Maven 打包 jar
能根据报错定位是配置、依赖、代码还是数据库问题
```

更进一步的标准：

```text
能把一个前端管理后台需要的接口完整设计出来
能写出稳定的分页查询和条件查询
能管理数据库 migration
能区分开发、测试、生产配置
能写少量单元测试和接口测试
能把服务部署到一台服务器或 Docker 容器里
```

## 18. 官方参考资料

优先看官方文档，遇到具体问题再搜索文章。

| 主题 | 地址 |
|---|---|
| Java 下载和版本 | https://www.oracle.com/java/technologies/downloads/ |
| Java SE 支持路线 | https://www.oracle.com/java/technologies/java-se-support-roadmap.html |
| OpenJDK | https://openjdk.org/ |
| Spring Boot | https://spring.io/projects/spring-boot |
| Spring Boot 系统要求 | https://docs.spring.io/spring-boot/system-requirements.html |
| Maven 快速入门 | https://maven.apache.org/guides/getting-started/maven-in-five-minutes.html |
| Maven Getting Started | https://maven.apache.org/guides/getting-started/ |
| Spring Data JPA | https://docs.spring.io/spring-data/jpa/reference/index.html |
| Spring Security JWT | https://docs.spring.io/spring-security/reference/servlet/oauth2/resource-server/jwt.html |

## 19. 最短实践路线

如果你不想看完整路线，可以先按这个最短路径走：

```text
第 1 天：看 Java class、interface、record、annotation
第 2 天：看 pom.xml，跑 mvn clean package
第 3 天：看 Controller，新增 /dev/ping
第 4 天：看 DTO，请求体和响应体
第 5 天：看 Entity/Repository，查一张表
第 6 天：新增一个 Note CRUD
第 7 天：给 Note CRUD 加 JWT 保护
第 8 天：打包 jar，用 java -jar 运行
```

这 8 天走完，你对 Java 后端的主干就会有感觉。后面再补细节，效率会比从语法书第一页开始高很多。
