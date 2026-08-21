# .net-ainame 项目目录结构说明

本文档从学习 .NET 的角度说明 `.net-ainame` 目录下每个文件的用途。路径均相对 `.net-ainame/` 根目录。

先抓住主线：这是一个 **Visual Studio 解决方案 + 一个 ASP.NET Core Web API 项目**。日常学习最该看的顺序是：

1. `Zhiliao.Ainame.sln`
2. `Zhiliao.Ainame.Api/Zhiliao.Ainame.Api.csproj`
3. `Zhiliao.Ainame.Api/Program.cs`
4. `Zhiliao.Ainame.Api/Controllers/`
5. `Zhiliao.Ainame.Api/Data/`、`Entities/`、`Contracts/`
6. `Options/`、`Services/`

`bin/` 和 `obj/` 是 `dotnet restore`、`dotnet build`、`dotnet run` 生成的文件，项目能从源码重新生成它们。它们已经逐个列出，但学习业务逻辑时可以先跳过。

## 顶层结构

```text
.net-ainame/
├── Zhiliao.Ainame.sln
├── README.md
├── docs/
│   ├── DEVELOPMENT.md
│   └── PROJECT_STRUCTURE.md
└── Zhiliao.Ainame.Api/
    ├── Program.cs
    ├── Zhiliao.Ainame.Api.csproj
    ├── Controllers/
    ├── Data/
    ├── Entities/
    ├── Contracts/
    ├── Options/
    ├── Services/
    ├── Properties/
    ├── bin/
    └── obj/
```

## 根目录与文档

| 文件 | 用途 |
|---|---|
| `.gitignore` | Git 忽略规则，排除 `bin/`、`obj/`、`.vs/`、本地用户配置等不应提交的文件。 |
| `README.md` | 项目快速入口，说明这是从 Python/FastAPI 迁移来的 .NET 后端，并给出最短启动步骤。 |
| `Zhiliao.Ainame.sln` | Visual Studio Solution 解决方案文件，当前只包含一个项目：`Zhiliao.Ainame.Api`。 |
| `docs/DEVELOPMENT.md` | 学习向开发指南，讲启动、技术栈、FastAPI 与 .NET 对照、调试、EF Core、JWT 等。 |
| `docs/PROJECT_STRUCTURE.md` | 本文档，专门解释目录结构和每个文件的用途。 |

## Web API 项目入口与配置

| 文件 | 用途 |
|---|---|
| `Zhiliao.Ainame.Api/Zhiliao.Ainame.Api.csproj` | .NET 项目文件。声明目标框架 `net9.0`、启用 nullable/implicit usings，并引用 BCrypt、MailKit、EF Core、MySQL、Redis、Swagger、ClosedXML 等 NuGet 包。 |
| `Zhiliao.Ainame.Api/Program.cs` | ASP.NET Core 应用入口。负责读取配置、注册依赖注入、配置 EF Core/MySQL、JWT 认证、Controller、Swagger、JSON snake_case，以及启动 HTTP 管道。 |
| `Zhiliao.Ainame.Api/appsettings.json` | 默认配置文件，包含日志级别、数据库连接串模板、JWT、Redis、SMTP 等配置。生产环境不应在这里放真实密钥。 |
| `Zhiliao.Ainame.Api/appsettings.Development.json` | 开发环境覆盖配置。当前设置了 Debug 日志、本地 MySQL 密码示例、本地 Redis、开发用 JWT 密钥。 |
| `Zhiliao.Ainame.Api/Zhiliao.Ainame.Api.http` | REST Client 请求示例文件，可在支持 `.http` 的编辑器中直接测试根路径、验证码、登录等接口。 |
| `Zhiliao.Ainame.Api/Properties/launchSettings.json` | 本地调试启动配置。定义 `http://localhost:5027`、Swagger 启动页 `/docs`，并设置 `ASPNETCORE_ENVIRONMENT=Development`。 |

## Controllers：HTTP 接口层

Controller 是请求入口，类似 FastAPI 的 router。它们接收 HTTP 请求，调用 DbContext 或 Service，并返回 JSON/文件。

| 文件 | 用途 |
|---|---|
| `Zhiliao.Ainame.Api/Controllers/AdminArtController.cs` | 文章后台 JSON/multipart 接口，提供 `/admin/insertArt`、`delArt`、`changeArt`、`queryArt`、`queryArtOut`；其中 `queryArt` 需要 JWT。 |
| `Zhiliao.Ainame.Api/Controllers/AdminArtFileController.cs` | 文章 Excel 导入导出接口，使用 ClosedXML 处理 `/admin/queryArtExcel` 和 `/admin/insertArtByExcel`。 |
| `Zhiliao.Ainame.Api/Controllers/AuthController.cs` | 认证接口，提供 `/auth/code` 发验证码、`/auth/register` 注册、`/auth/login` 登录并返回 JWT。 |
| `Zhiliao.Ainame.Api/Controllers/CompanyController.cs` | 公司模块接口，提供 `/company/create`、`query`、`update`、`delete`，删除公司时清理关联订单和明细。 |
| `Zhiliao.Ainame.Api/Controllers/CourseController.cs` | 课程 CRUD 接口，提供 `/course` 的增删改查，并包含课程实体到 DTO 的映射方法。 |
| `Zhiliao.Ainame.Api/Controllers/NameController.cs` | 起名接口 `/name`，当前是固定示例/mock 返回，后续可接入真实起名算法或大模型。 |
| `Zhiliao.Ainame.Api/Controllers/OrderController.cs` | 订单模块接口，提供创建、更新、查询、删除订单；订单由订单头和订单明细组成。 |
| `Zhiliao.Ainame.Api/Controllers/ProductController.cs` | 产品模块接口，提供 `/product/create`、`query`、`update`、`delete`；删除参数 `prduct_id` 保持与旧 Python 接口兼容。 |
| `Zhiliao.Ainame.Api/Controllers/RegionController.cs` | 省市区接口，提供 `/region/provinces`、`cities`、`districts`、`init`，数据来自 Redis。 |
| `Zhiliao.Ainame.Api/Controllers/RootController.cs` | 根路径、问候、邮件测试接口，包含 `/`、`/hello/{name}`、`/mail/test`。 |
| `Zhiliao.Ainame.Api/Controllers/SchoolController.cs` | 学校 CRUD 接口，删除学校时先清理相关学生选课，再删除学校及关联教师/学生。 |
| `Zhiliao.Ainame.Api/Controllers/StudentController.cs` | 学生 CRUD 接口，列表和详情会通过 join 查询附带学生选课与成绩。 |
| `Zhiliao.Ainame.Api/Controllers/StudentCourseController.cs` | 学生选课中间表接口，支持批量替换选课、单条选课、按课程查学生、查询/更新/删除选课记录。 |
| `Zhiliao.Ainame.Api/Controllers/TeacherController.cs` | 班主任 CRUD 接口，可按 `school_id` 过滤，删除班主任时会先清理其学生选课。 |

## Data、Entities、Contracts、Options、Services

这些文件是项目的业务骨架：实体描述数据库表，DTO 描述接口 JSON，Service 封装可复用能力。

| 文件 | 用途 |
|---|---|
| `Zhiliao.Ainame.Api/Data/AppDbContext.cs` | EF Core 数据库上下文。集中声明 `DbSet<T>`，并用 Fluent API 配置表名、唯一索引、外键关系、级联/限制删除行为。 |
| `Zhiliao.Ainame.Api/Entities/AppUser.cs` | 用户实体，对应 `user` 表，包含邮箱、用户名、密码哈希；密码列映射到 `_password`。 |
| `Zhiliao.Ainame.Api/Entities/Art.cs` | 文章实体，对应 `art` 表，包含用户名、性别、正文、缩略图二进制、创建时间。 |
| `Zhiliao.Ainame.Api/Entities/EmailCode.cs` | 邮箱验证码实体，对应 `email_code` 表，用于注册验证码校验。 |
| `Zhiliao.Ainame.Api/Entities/OrderEntities.cs` | 订单域实体集合，定义公司、产品、订单头、订单明细及导航属性。 |
| `Zhiliao.Ainame.Api/Entities/SchoolEntities.cs` | 校园域实体集合，定义学校、教师、学生、课程、学生选课中间表。 |
| `Zhiliao.Ainame.Api/Contracts/ApiDtos.cs` | 认证和起名模块的请求/响应 DTO，如注册、登录、用户信息、起名请求与结果。 |
| `Zhiliao.Ainame.Api/Contracts/MigrationDtos.cs` | 从 FastAPI 迁移来的文章、校园、订单、省市区等模块 DTO，包含输入校验和旧前端兼容字段。 |
| `Zhiliao.Ainame.Api/Options/JwtOptions.cs` | JWT 强类型配置类，绑定 `appsettings` 中的 `Jwt` 节点。 |
| `Zhiliao.Ainame.Api/Options/SmtpOptions.cs` | SMTP 强类型配置类，绑定 `appsettings` 中的 `Smtp` 节点。 |
| `Zhiliao.Ainame.Api/Services/IEmailSender.cs` | 邮件发送抽象接口，Controller 依赖它而不是直接依赖 SMTP 实现。 |
| `Zhiliao.Ainame.Api/Services/IJwtTokenService.cs` | JWT 服务抽象接口，定义签发访问令牌/刷新令牌、解析用户 id 等能力。 |
| `Zhiliao.Ainame.Api/Services/JwtTokenService.cs` | JWT 服务实现，使用 HMAC-SHA256 签发和校验 token，并保持与 Python 版 payload 约定兼容。 |
| `Zhiliao.Ainame.Api/Services/RegionDataService.cs` | 省市区 Redis 服务，负责初始化示例行政区划数据，并按省/市/区读取列表。 |
| `Zhiliao.Ainame.Api/Services/SmtpEmailSender.cs` | MailKit SMTP 邮件发送实现，用于验证码邮件和 `/mail/test`。 |

## bin/Debug/net9.0：运行输出与依赖

`bin/Debug/net9.0/` 是 Debug 编译后的运行目录。里面既有本项目编译结果，也有 NuGet 依赖 DLL 和复制过来的配置文件。

| 文件 | 用途 |
|---|---|
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/appsettings.Development.json` | 从项目目录复制到运行目录的开发环境配置，程序运行时可读取。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/appsettings.json` | 从项目目录复制到运行目录的默认配置。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/BCrypt.Net-Next.dll` | BCrypt 密码哈希库，用于注册和登录密码校验。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/BouncyCastle.Cryptography.dll` | 加密算法库，作为部分依赖包的底层加密支持。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ClosedXML.dll` | Excel `.xlsx` 读写库，文章 Excel 导入导出使用它。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ClosedXML.Parser.dll` | ClosedXML 的公式/内容解析辅助组件。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/DocumentFormat.OpenXml.dll` | OpenXML SDK，支撑 Office 文档格式读写。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/DocumentFormat.OpenXml.Framework.dll` | OpenXML SDK 框架组件，ClosedXML 间接使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ExcelNumberFormat.dll` | Excel 数字格式解析库，ClosedXML 依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Humanizer.dll` | 文本格式化/人性化显示库，主要来自 EF Core 设计时依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/MailKit.dll` | SMTP/IMAP/POP 邮件客户端库，`SmtpEmailSender` 使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.AspNetCore.Authentication.JwtBearer.dll` | ASP.NET Core JWT Bearer 认证中间件。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.AspNetCore.OpenApi.dll` | ASP.NET Core OpenAPI 支持组件。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.Bcl.AsyncInterfaces.dll` | 异步接口兼容库，供部分 NuGet 包使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.Build.Locator.dll` | 定位 MSBuild 的辅助库，常由 Roslyn/EF 设计时组件使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.CodeAnalysis.CSharp.dll` | Roslyn C# 编译器 API。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.CodeAnalysis.CSharp.Workspaces.dll` | Roslyn C# Workspace API，设计时/工具链依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.CodeAnalysis.dll` | Roslyn 编译平台核心库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.CodeAnalysis.Workspaces.dll` | Roslyn Workspace 核心库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.dll` | Roslyn MSBuild Workspace 构建宿主。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.CodeAnalysis.Workspaces.MSBuild.dll` | Roslyn 与 MSBuild 项目系统集成库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.EntityFrameworkCore.Abstractions.dll` | EF Core 抽象层。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.EntityFrameworkCore.Design.dll` | EF Core 设计时工具支持，如迁移脚手架。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.EntityFrameworkCore.dll` | EF Core ORM 核心库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.EntityFrameworkCore.Relational.dll` | EF Core 关系型数据库通用支持。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.Extensions.DependencyModel.dll` | 依赖模型读取库，用于运行时/工具读取依赖信息。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.IdentityModel.Abstractions.dll` | Microsoft IdentityModel 抽象库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.IdentityModel.JsonWebTokens.dll` | JWT 读取、写入、校验相关库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.IdentityModel.Logging.dll` | IdentityModel 日志辅助库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.IdentityModel.Protocols.dll` | 身份认证协议通用支持库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.IdentityModel.Protocols.OpenIdConnect.dll` | OpenID Connect 协议支持库，JWT 认证链路可能间接依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.IdentityModel.Tokens.dll` | token 签名、密钥、校验参数等核心库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Microsoft.OpenApi.dll` | OpenAPI 对象模型库，Swagger 生成使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/MimeKit.dll` | MIME 邮件消息构造库，MailKit 发信使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Mono.TextTemplating.dll` | 文本模板处理库，常见于 EF/Roslyn 设计时依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/MySqlConnector.dll` | MySQL ADO.NET 驱动，Pomelo EF Core provider 底层使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Pipelines.Sockets.Unofficial.dll` | 高性能 socket pipeline 辅助库，Redis 客户端依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Pomelo.EntityFrameworkCore.MySql.dll` | EF Core 的 MySQL Provider，负责把 LINQ 翻译为 MySQL SQL。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/RBush.dll` | 空间索引/树结构辅助库，来自文档/Excel 相关依赖链。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/SixLabors.Fonts.dll` | 字体处理库，ClosedXML 等组件在测量/渲染字体时可能使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/StackExchange.Redis.dll` | Redis 客户端库，省市区接口使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Swashbuckle.AspNetCore.Swagger.dll` | Swagger/OpenAPI 文档对象生成核心库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Swashbuckle.AspNetCore.SwaggerGen.dll` | Swagger 文档生成器，扫描 Controller 和模型。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Swashbuckle.AspNetCore.SwaggerUI.dll` | Swagger UI 静态资源与中间件支持。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.CodeDom.dll` | CodeDOM 代码生成/编译抽象，部分设计时工具依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.Composition.AttributedModel.dll` | MEF/Composition 组件模型库，Roslyn 设计时依赖。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.Composition.Convention.dll` | MEF 约定式组合支持库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.Composition.Hosting.dll` | MEF 组合宿主库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.Composition.Runtime.dll` | MEF 运行时库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.Composition.TypedParts.dll` | MEF typed parts 支持库。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.IdentityModel.Tokens.Jwt.dll` | .NET JWT 标准处理库，`JwtTokenService` 使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/System.IO.Packaging.dll` | Open Packaging Convention 支持库，OpenXML/Excel 读写使用。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Zhiliao.Ainame.Api.deps.json` | 应用依赖清单，运行时据此定位 NuGet 依赖和程序集。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Zhiliao.Ainame.Api.dll` | 本项目编译后的主程序集，包含业务代码 IL。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Zhiliao.Ainame.Api.exe` | Windows 可执行宿主，用来启动本项目。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Zhiliao.Ainame.Api.pdb` | 调试符号文件，断点、调用栈、源码行号映射依赖它。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Zhiliao.Ainame.Api.runtimeconfig.json` | 运行时配置，声明目标 .NET 版本等信息。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/Zhiliao.Ainame.Api.staticwebassets.endpoints.json` | 静态 Web 资源端点清单，Swagger UI 等静态资源相关。 |

## bin/Debug/net9.0：本地化资源 DLL

这些文件是 Roslyn/MSBuild/编译器工具链的多语言资源包，主要用于本地化诊断消息。它们不是本项目手写业务代码。

| 文件 | 用途 |
|---|---|
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/cs/Microsoft.CodeAnalysis.CSharp.resources.dll` | 捷克语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/cs/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 捷克语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/cs/Microsoft.CodeAnalysis.resources.dll` | 捷克语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/cs/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 捷克语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/cs/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 捷克语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/de/Microsoft.CodeAnalysis.CSharp.resources.dll` | 德语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/de/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 德语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/de/Microsoft.CodeAnalysis.resources.dll` | 德语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/de/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 德语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/de/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 德语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/es/Microsoft.CodeAnalysis.CSharp.resources.dll` | 西班牙语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/es/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 西班牙语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/es/Microsoft.CodeAnalysis.resources.dll` | 西班牙语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/es/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 西班牙语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/es/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 西班牙语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/fr/Microsoft.CodeAnalysis.CSharp.resources.dll` | 法语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/fr/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 法语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/fr/Microsoft.CodeAnalysis.resources.dll` | 法语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/fr/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 法语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/fr/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 法语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/it/Microsoft.CodeAnalysis.CSharp.resources.dll` | 意大利语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/it/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 意大利语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/it/Microsoft.CodeAnalysis.resources.dll` | 意大利语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/it/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 意大利语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/it/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 意大利语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ja/Microsoft.CodeAnalysis.CSharp.resources.dll` | 日语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ja/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 日语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ja/Microsoft.CodeAnalysis.resources.dll` | 日语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ja/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 日语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ja/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 日语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ko/Microsoft.CodeAnalysis.CSharp.resources.dll` | 韩语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ko/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 韩语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ko/Microsoft.CodeAnalysis.resources.dll` | 韩语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ko/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 韩语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ko/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 韩语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pl/Microsoft.CodeAnalysis.CSharp.resources.dll` | 波兰语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pl/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 波兰语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pl/Microsoft.CodeAnalysis.resources.dll` | 波兰语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pl/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 波兰语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pl/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 波兰语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pt-BR/Microsoft.CodeAnalysis.CSharp.resources.dll` | 巴西葡萄牙语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pt-BR/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 巴西葡萄牙语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pt-BR/Microsoft.CodeAnalysis.resources.dll` | 巴西葡萄牙语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pt-BR/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 巴西葡萄牙语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/pt-BR/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 巴西葡萄牙语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ru/Microsoft.CodeAnalysis.CSharp.resources.dll` | 俄语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ru/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 俄语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ru/Microsoft.CodeAnalysis.resources.dll` | 俄语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ru/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 俄语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/ru/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 俄语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/tr/Microsoft.CodeAnalysis.CSharp.resources.dll` | 土耳其语 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/tr/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 土耳其语 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/tr/Microsoft.CodeAnalysis.resources.dll` | 土耳其语 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/tr/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 土耳其语 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/tr/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 土耳其语 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hans/Microsoft.CodeAnalysis.CSharp.resources.dll` | 简体中文 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hans/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 简体中文 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hans/Microsoft.CodeAnalysis.resources.dll` | 简体中文 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hans/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 简体中文 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hans/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 简体中文 Roslyn Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hant/Microsoft.CodeAnalysis.CSharp.resources.dll` | 繁体中文 C# 编译器资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hant/Microsoft.CodeAnalysis.CSharp.Workspaces.resources.dll` | 繁体中文 C# Workspace 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hant/Microsoft.CodeAnalysis.resources.dll` | 繁体中文 Roslyn 核心资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hant/Microsoft.CodeAnalysis.Workspaces.MSBuild.BuildHost.resources.dll` | 繁体中文 Roslyn MSBuild BuildHost 资源。 |
| `Zhiliao.Ainame.Api/bin/Debug/net9.0/zh-Hant/Microsoft.CodeAnalysis.Workspaces.resources.dll` | 繁体中文 Roslyn Workspace 资源。 |

## obj：还原与编译中间文件

`obj/` 是 MSBuild/NuGet 的中间目录。它保存依赖解析结果、生成的源码、缓存、临时程序集等；删掉后可通过 `dotnet restore` 和 `dotnet build` 再生成。

| 文件 | 用途 |
|---|---|
| `Zhiliao.Ainame.Api/obj/project.assets.json` | NuGet restore 生成的依赖资产图，记录所有包、版本、目标框架和运行时资产。 |
| `Zhiliao.Ainame.Api/obj/project.nuget.cache` | NuGet restore 缓存状态，用于判断依赖解析是否需要重新执行。 |
| `Zhiliao.Ainame.Api/obj/Zhiliao.Ainame.Api.csproj.nuget.dgspec.json` | NuGet 依赖图规格文件，restore 时描述项目和包依赖关系。 |
| `Zhiliao.Ainame.Api/obj/Zhiliao.Ainame.Api.csproj.nuget.g.props` | NuGet 生成的 MSBuild props 文件，把包相关属性接入构建。 |
| `Zhiliao.Ainame.Api/obj/Zhiliao.Ainame.Api.csproj.nuget.g.targets` | NuGet 生成的 MSBuild targets 文件，把包相关构建目标接入构建。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/.NETCoreApp,Version=v9.0.AssemblyAttributes.cs` | 自动生成的目标框架程序集特性源码。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/apphost.exe` | 中间阶段生成的 Windows 应用宿主。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/ref/Zhiliao.Ainame.Api.dll` | 编译产生的 reference assembly，供其他项目引用时使用类型信息。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/refint/Zhiliao.Ainame.Api.dll` | 中间 reference assembly，供本次构建内部使用。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/rjsmcshtml.dswa.cache.json` | Razor/静态 Web 资源构建缓存，记录 `.cshtml` 相关扫描结果。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/rjsmrazor.dswa.cache.json` | Razor/静态 Web 资源构建缓存，记录 `.razor` 相关扫描结果。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/rpswa.dswa.cache.json` | Razor/静态 Web 资源构建缓存，记录项目静态资源扫描结果。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/staticwebassets.build.endpoints.json` | 构建期静态 Web 资源端点清单。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/staticwebassets.build.json` | 构建期静态 Web 资源清单，Swagger UI 等资源会参与该机制。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/staticwebassets.build.json.cache` | 静态 Web 资源清单生成缓存。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao..80C10642.Up2Date` | MSBuild 增量构建标记，用于判断某些步骤是否已是最新。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.AssemblyInfo.cs` | 自动生成的程序集信息源码，如版本、公司、产品名等属性。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.AssemblyInfoInputs.cache` | AssemblyInfo 生成输入缓存。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.assets.cache` | 项目资产缓存，辅助 MSBuild 快速判断依赖变更。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.csproj.AssemblyReference.cache` | 程序集引用解析缓存。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.csproj.CoreCompileInputs.cache` | C# 核心编译输入缓存，用于增量编译。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.csproj.FileListAbsolute.txt` | 构建输出文件的绝对路径列表，清理和增量构建会用到。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.dll` | 中间编译产物，随后会复制到 `bin/Debug/net9.0/`。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.GeneratedMSBuildEditorConfig.editorconfig` | MSBuild 自动生成的编译器/analyzer 配置。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.genruntimeconfig.cache` | runtimeconfig 生成缓存。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.GlobalUsings.g.cs` | 因 csproj 开启 `ImplicitUsings` 自动生成的全局 using 源码。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.MvcApplicationPartsAssemblyInfo.cache` | MVC Application Parts 生成缓存。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.MvcApplicationPartsAssemblyInfo.cs` | MVC 自动生成的程序集元数据，用于发现 Controller/Application Part。 |
| `Zhiliao.Ainame.Api/obj/Debug/net9.0/Zhiliao.Ainame.Api.pdb` | 中间调试符号文件，随后会复制到 `bin/Debug/net9.0/`。 |

## 学习时的阅读建议

第一次读这个项目，不建议从 `bin/` 或 `obj/` 开始。更顺的路径是：

1. 先看 `README.md` 和 `docs/DEVELOPMENT.md`，知道怎么启动。
2. 看 `Zhiliao.Ainame.Api.csproj`，认识项目依赖。
3. 看 `Program.cs`，理解 .NET Web API 的启动、依赖注入、中间件、认证、Swagger。
4. 选一个 Controller，例如 `RootController.cs` 或 `AuthController.cs`，顺着请求看进去。
5. 读 `AppDbContext.cs` 和 `Entities/`，理解 C# 类如何映射数据库表。
6. 回头看 `Contracts/`，理解前后端 JSON 入参/出参怎么定义。
