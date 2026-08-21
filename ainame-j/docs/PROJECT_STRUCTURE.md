# ainame-j 项目目录结构说明

本文档说明 `ainame-j` 每个文件的用途。路径均相对 `ainame-j/` 根目录。

## 顶层结构

```text
ainame-j/
├── pom.xml
├── README.md
├── docs/
├── src/main/java/com/zhiliao/ainame/
│   ├── config/
│   ├── controller/
│   ├── dto/
│   ├── entity/
│   ├── repository/
│   └── service/
└── src/main/resources/
```

## 根目录与文档

| 文件 | 用途 |
|---|---|
| `.gitignore` | Git 忽略规则，排除 `target/`、IDE 配置、本地私有配置等。 |
| `pom.xml` | Maven 项目文件，声明 Java 21、Spring Boot、MySQL、Redis、Security、JWT、Apache POI、springdoc 等依赖。 |
| `README.md` | 项目快速入口，说明技术栈、启动命令、默认端口和文档位置。 |
| `docs/DEVELOPMENT.md` | 开发指南，包含启动、配置、技术栈对照、路由表和阅读顺序。 |
| `docs/JS_TO_JAVA_SPRING.md` | 给前端/JS 开发者看的 Java/Spring Boot 概念对照。 |
| `docs/PROJECT_STRUCTURE.md` | 本文件，逐个说明项目文件用途。 |
| `docs/FRONTEND_TO_JAVA_ROADMAP.md` | 给前端开发者看的 Java 后端学习路线，包含阶段计划、项目练习和版本选择说明。 |

## 启动与配置

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/AinameJavaApplication.java` | Spring Boot 应用入口，调用 `SpringApplication.run` 启动内嵌 Tomcat 和 Spring 容器。 |
| `src/main/resources/application.yml` | 默认配置，包含端口、MySQL、JPA、Redis、邮件、Swagger、JWT 等配置。 |
| `src/main/resources/application-dev.yml` | 开发环境覆盖配置，当前主要覆盖本地 MySQL 密码和日志级别。 |

## config：框架配置

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/config/GlobalExceptionHandler.java` | 全局异常处理，把校验错误、业务异常转成 `{ "detail": "..." }` 风格响应。 |
| `src/main/java/com/zhiliao/ainame/config/JwtAuthenticationFilter.java` | JWT 过滤器，从 `Authorization: Bearer ...` 解析访问令牌并写入 Spring Security 上下文。 |
| `src/main/java/com/zhiliao/ainame/config/OpenApiConfig.java` | Swagger/OpenAPI 配置，设置 API 标题、版本和 Bearer JWT 鉴权说明。 |
| `src/main/java/com/zhiliao/ainame/config/SecurityConfig.java` | Spring Security 配置，关闭 session/csrf，让 `/admin/queryArt` 需要 JWT，其它接口默认放行。 |

## controller：HTTP 接口层

Controller 对应 `.net-ainame` 的 `Controllers/`，也类似 FastAPI 的 router。

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/controller/AdminArtController.java` | 文章后台接口，处理文章上传、删除、修改、查询，其中 `/admin/queryArt` 由 Security 保护。 |
| `src/main/java/com/zhiliao/ainame/controller/AdminArtFileController.java` | 文章 Excel 导入导出，使用 Apache POI 生成和解析 `.xlsx/.xls`。 |
| `src/main/java/com/zhiliao/ainame/controller/AuthController.java` | 认证接口，提供验证码、注册、登录，注册使用 BCrypt，登录返回 JWT。 |
| `src/main/java/com/zhiliao/ainame/controller/CompanyController.java` | 公司接口，提供创建、查询、更新、删除，并在删除时清理关联订单。 |
| `src/main/java/com/zhiliao/ainame/controller/CourseController.java` | 课程 CRUD 接口，删除课程前先清理学生选课记录。 |
| `src/main/java/com/zhiliao/ainame/controller/NameController.java` | 起名接口 `/name`，当前返回固定示例，保留后续接入算法/大模型的位置。 |
| `src/main/java/com/zhiliao/ainame/controller/OrderController.java` | 订单接口，处理订单头、订单明细的创建、更新、查询和删除。 |
| `src/main/java/com/zhiliao/ainame/controller/ProductController.java` | 产品接口，保留历史参数名 `prduct_id`，删除产品时清理关联订单明细。 |
| `src/main/java/com/zhiliao/ainame/controller/RegionController.java` | 省市区接口，使用 Redis 存储示例省/市/区数据，保留 `province_code`、`city_code` 参数名。 |
| `src/main/java/com/zhiliao/ainame/controller/RootController.java` | 根路径、hello、邮件测试接口，对应 `/`、`/hello/{name}`、`/mail/test`。 |
| `src/main/java/com/zhiliao/ainame/controller/SchoolController.java` | 学校 CRUD 接口，删除学校时先清理相关学生选课。 |
| `src/main/java/com/zhiliao/ainame/controller/StudentController.java` | 学生 CRUD 接口，查询时附带课程和成绩。 |
| `src/main/java/com/zhiliao/ainame/controller/StudentCourseController.java` | 学生选课接口，支持批量替换、单条创建、查询、更新成绩和删除。 |
| `src/main/java/com/zhiliao/ainame/controller/TeacherController.java` | 班主任 CRUD 接口，可按 `school_id` 过滤，删除时清理其学生选课。 |

## dto：请求/响应模型

DTO 对应 `.net-ainame` 的 `Contracts/`，用于描述 API JSON，不直接等于数据库表。

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/dto/ArtDtos.java` | 文章模块 DTO：删除、修改、分页查询、文章输出、包装响应。 |
| `src/main/java/com/zhiliao/ainame/dto/AuthDtos.java` | 认证模块 DTO：注册、登录、用户信息、登录响应。 |
| `src/main/java/com/zhiliao/ainame/dto/CommonDtos.java` | 通用 DTO，如 `ResponseOut` 和简单包装消息。 |
| `src/main/java/com/zhiliao/ainame/dto/NameDtos.java` | 起名模块 DTO：起名请求、推荐名、响应列表。 |
| `src/main/java/com/zhiliao/ainame/dto/OrderDtos.java` | 订单域 DTO：公司、产品、订单创建/查询响应。 |
| `src/main/java/com/zhiliao/ainame/dto/RegionDtos.java` | 省市区 DTO：行政区划项和列表包装。 |
| `src/main/java/com/zhiliao/ainame/dto/SchoolDtos.java` | 校园域 DTO：学校、教师、学生、课程、选课、成绩相关请求/响应。 |

## entity：JPA 数据库模型

Entity 对应数据库表，使用 JPA 注解显式映射表名和列名。

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/entity/AppUser.java` | 用户表 `user`，包含邮箱、用户名、`_password` 密码哈希。 |
| `src/main/java/com/zhiliao/ainame/entity/Art.java` | 文章表 `art`，包含正文、性别、缩略图二进制和创建时间。 |
| `src/main/java/com/zhiliao/ainame/entity/Company.java` | 公司表 `company`，与订单头是一对多关系。 |
| `src/main/java/com/zhiliao/ainame/entity/Course.java` | 课程表 `course`，用于学生选课。 |
| `src/main/java/com/zhiliao/ainame/entity/EmailCode.java` | 邮箱验证码表 `email_code`，注册时验证最新验证码。 |
| `src/main/java/com/zhiliao/ainame/entity/OrderHeader.java` | 订单头表 `order`，包含订单编号、公司 ID、创建时间。 |
| `src/main/java/com/zhiliao/ainame/entity/OrderLine.java` | 订单明细表 `order_product`，表示某订单购买某产品的数量。 |
| `src/main/java/com/zhiliao/ainame/entity/Product.java` | 产品表 `product`，包含单价、库存、描述、产品编号。 |
| `src/main/java/com/zhiliao/ainame/entity/School.java` | 学校表 `school`，与教师是一对多关系。 |
| `src/main/java/com/zhiliao/ainame/entity/Student.java` | 学生表 `student`，归属班主任。 |
| `src/main/java/com/zhiliao/ainame/entity/StudentCourse.java` | 学生选课中间表 `student_course`，包含学生、课程、成绩。 |
| `src/main/java/com/zhiliao/ainame/entity/Teacher.java` | 班主任表 `teacher`，归属学校，拥有学生。 |

## repository：数据访问层

Repository 对应 .NET 里的 `DbSet<T>` 常用入口。Spring Data JPA 会根据接口和方法名自动实现查询。

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/repository/AppUserRepository.java` | 用户查询，支持按邮箱查询和判断邮箱是否存在。 |
| `src/main/java/com/zhiliao/ainame/repository/ArtRepository.java` | 文章查询和批量删除。 |
| `src/main/java/com/zhiliao/ainame/repository/CompanyRepository.java` | 公司 CRUD 与按 ID 排序查询。 |
| `src/main/java/com/zhiliao/ainame/repository/CourseRepository.java` | 课程 CRUD 与按 ID 排序查询。 |
| `src/main/java/com/zhiliao/ainame/repository/EmailCodeRepository.java` | 邮箱验证码查询，按邮箱和验证码取最新一条。 |
| `src/main/java/com/zhiliao/ainame/repository/OrderHeaderRepository.java` | 订单头 CRUD、按公司查订单、批量删除。 |
| `src/main/java/com/zhiliao/ainame/repository/OrderLineRepository.java` | 订单明细 CRUD，按订单/产品查询和删除。 |
| `src/main/java/com/zhiliao/ainame/repository/ProductRepository.java` | 产品 CRUD 与按 ID 排序查询。 |
| `src/main/java/com/zhiliao/ainame/repository/SchoolRepository.java` | 学校 CRUD 与按 ID 排序查询。 |
| `src/main/java/com/zhiliao/ainame/repository/StudentCourseRepository.java` | 学生选课查询、去重判断、按学生/课程删除。 |
| `src/main/java/com/zhiliao/ainame/repository/StudentRepository.java` | 学生 CRUD，支持按班主任查询、按班主任集合查询。 |
| `src/main/java/com/zhiliao/ainame/repository/TeacherRepository.java` | 教师 CRUD，支持按学校查询。 |

## service：可复用服务层

| 文件 | 用途 |
|---|---|
| `src/main/java/com/zhiliao/ainame/service/EmailSender.java` | 邮件发送接口，Controller 只依赖抽象。 |
| `src/main/java/com/zhiliao/ainame/service/JwtTokenService.java` | JWT 签发和校验服务，兼容旧项目的 `iss=userId`、`sub=1/2` 约定。 |
| `src/main/java/com/zhiliao/ainame/service/RegionDataService.java` | Redis 省市区服务，初始化示例数据并读取省/市/区列表。 |
| `src/main/java/com/zhiliao/ainame/service/SmtpEmailSender.java` | Spring Mail 邮件发送实现，用于验证码和邮件测试。 |

## 生成目录

运行 Maven 后会出现：

```text
target/
```

它类似前端项目的 `dist/` 或 .NET 的 `bin/obj`，是构建产物，不需要提交。
