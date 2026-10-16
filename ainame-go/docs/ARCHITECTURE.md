# 源项目架构摘要

迁移依据：同级目录 `ainame-j` 的 Java 源码、Maven 配置与 Spring 路由。Java 项目以 Spring Boot MVC 为 HTTP 层、MyBatis-Plus 为数据访问、MySQL 为主要数据库，并集成 JWT、安全过滤器、Redis、SMTP、Excel 和 OpenAPI。默认 API 端口在 Java 配置中是 8000（README 中部分旧说明另有端口，运行时以配置为准）。

主要业务域：

- **基础/认证**：根、hello、邮件测试；邮箱验证码、注册、登录、JWT。
- **起名**：`POST /name`，目前是 mock 示例响应。
- **文章管理**：`/admin` 下增删改查、分页、Excel 上传下载。
- **区域**：省/市/区查询与初始化，依赖 Redis。
- **教学**：学校、教师、学生、课程、学生选课/成绩。
- **交易示例**：公司、产品、订单头与订单明细。

完整路由请对照 `ainame-j/src/main/java/com/zhiliao/ainame/controller`。数据模型和 JSON 字段应以 DTO/entity 和真实客户端契约为准，不能只根据控制器名猜测。迁移时尤其需要验证状态码、字段命名、空值语义、分页格式、历史拼写参数等兼容点。
