# 知了 AI 起名 — .NET 后端开发指南（学习向）

本文档面向**以学习为目的**的读者：不仅说明「怎么跑」，还说明 **.NET 技术栈里各块是什么、在本项目里怎么串起来**，并给出**可照着做的开发步骤**。若你熟悉 Python 的 FastAPI + SQLAlchemy，文中会刻意做**概念对照**，便于迁移心智模型。

---

## 启动项目（具体操作）

**目标**：在本机把 API 跑起来，浏览器能打开 Swagger（`/docs`）并调用接口。下面按顺序做即可；路径请改成你电脑上的真实路径。

### 0. 启动前先确认三件事

| 检查项 | 怎么确认 | 不做会怎样 |
|--------|----------|------------|
| **.NET 9 SDK** | 打开终端执行 `dotnet --version`，应显示 **9.x.x** | 无法编译、无法运行 |
| **MySQL** | 服务已启动，且存在数据库 **`zhiliao_ainame`**（表可与 Python 项目 Alembic 一致） | 一访问读写库的接口就报错 |
| **Redis** | 本机 `127.0.0.1:6379` 可连接（或用工具改 `Redis:ConnectionString`） | **`/region/*` 省市区接口会失败**；认证、校园、订单等不依赖 Redis 的仍可测 |

### 1. 进入正确的目录（很重要）

必须在包含 **`Zhiliao.Ainame.sln`** 和文件夹 **`Zhiliao.Ainame.Api`** 的那一层执行命令，不要进到更深层就 `dotnet run`。

**PowerShell 示例**（请替换为你的路径）：

```powershell
Set-Location "C:\Users\Administrator\Desktop\pythontest\.net-ainame"
```

> **注意**：在 Windows PowerShell 5.x 里，**不要用** `cd 某路径 && dotnet run`（`&&` 常报错）。请分行执行，或升级 PowerShell 7+。

### 2. 配置数据库（必做）

用编辑器打开：

`Zhiliao.Ainame.Api/appsettings.Development.json`

把 `ConnectionStrings:DefaultConnection` 里的 **密码** 改成你的 MySQL 密码，并确认 **库名**、**端口** 与你的实例一致，例如：

```json
"ConnectionStrings": {
  "DefaultConnection": "Server=127.0.0.1;Port=3306;Database=zhiliao_ainame;User=root;Password=这里改成你的密码;SslMode=None;CharSet=utf8mb4"
}
```

- 若库里**还没有表**：可沿用 Python 项目 `zhiliao-ainame` 的 Alembic 迁移建好表，再让 .NET 指向同一库。
- 运行时会加载 **Development** 配置：`ASPNETCORE_ENVIRONMENT` 默认为 Development（见 `Properties/launchSettings.json`），因此改 **`appsettings.Development.json`** 即可，一般不必动生产用的 `appsettings.json`。

### 3. Redis、邮件（按需要）

| 配置位置 | 键 | 说明 |
|----------|-----|------|
| `appsettings.json` 或 `appsettings.Development.json` | `Redis:ConnectionString` | 默认 `127.0.0.1:6379`；不配或 Redis 未启动时，**不要测 `/region/*`** |
| 同上 | `Smtp:*` | 不配则 **`/auth/code` 发信**、**`/mail/test`** 会失败，属正常 |

### 4. 还原依赖、编译、运行

在 **`.net-ainame` 根目录**依次执行：

```powershell
dotnet restore
dotnet build
dotnet run --project .\Zhiliao.Ainame.Api\Zhiliao.Ainame.Api.csproj
```

若当前目录已是根目录，也可写：

```powershell
dotnet run --project Zhiliao.Ainame.Api
```

### 5. 怎样算启动成功

终端出现类似日志（具体文字可能随版本略有不同）：

```text
Now listening on: http://localhost:5027
Application started. Press Ctrl+C to shut down.
```

**默认 HTTP 端口是 `5027`**，定义在 `Zhiliao.Ainame.Api/Properties/launchSettings.json` 的 `applicationUrl`。若端口被占用，改该文件里的端口后重新运行。

### 6. 浏览器里要打开的地址

| URL | 预期 |
|-----|------|
| http://localhost:5027/ | JSON 含 `message`: `Hello World`（本项目 JSON 为 snake_case 风格） |
| http://localhost:5027/docs | **Swagger UI**，用来调试所有接口（本项目故意挂在 `/docs`，对齐 FastAPI 习惯） |

### 7. 改代码后自动重启（可选）

```powershell
dotnet watch run --project .\Zhiliao.Ainame.Api\Zhiliao.Ainame.Api.csproj
```

保存 `.cs` 等文件后会自动重新编译并启动。

### 8. 用 Visual Studio 启动（可选）

1. 双击打开 **`Zhiliao.Ainame.sln`**。  
2. 将启动项目设为 **Zhiliao.Ainame.Api**，运行配置选 **http**（与 `launchSettings.json` 一致）。  
3. 按 **F5**；一般会打开浏览器到 `http://localhost:5027/docs`。

### 9. 不想把密码写进 JSON 时（推荐练习）

在 **`Zhiliao.Ainame.Api`** 目录下执行（只需做一次 `init`）：

```powershell
cd Zhiliao.Ainame.Api
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Server=127.0.0.1;Port=3306;Database=zhiliao_ainame;User=root;Password=你的密码;SslMode=None;CharSet=utf8mb4"
```

User Secrets 存在用户目录，**不会进 Git**。更多键名见下文第 6.3 节。

### 10. 启动失败时

常见原因：**MySQL 未启动或密码/库名不对**（改 `appsettings.Development.json` 或 User Secrets）、**5027 端口被占用**（改 `Properties/launchSettings.json` 里 `applicationUrl`）、**只测省市区却未开 Redis**（先不测 `/region/*`，或启动 Redis）。更系统的清单见 **[第 13 节：故障排查清单](#13-故障排查清单)**。

---

## 1. 文档怎么读、工程在哪里

| 你现在的位置 | 含义 |
|-------------|------|
| 仓库目录 `pythontest/.net-ainame/` | 本 .NET 后端的**根目录**（与 Python 项目 `zhiliao-ainame` 并列） |
| `Zhiliao.Ainame.sln` | **解决方案（Solution）**：一个或多个项目的容器，Visual Studio / Rider 通常打开它 |
| `Zhiliao.Ainame.Api/` | **ASP.NET Core Web API 项目**：实际运行的网站程序 |
| `Zhiliao.Ainame.Api/Program.cs` | **程序入口**：注册服务、中间件、启动 Kestrel 服务器 |
| `docs/DEVELOPMENT.md` | 本文件：开发与学习说明 |

建议阅读顺序：**先按上文《启动项目（具体操作）》把项目跑起来 → 第 2 节（技术栈地图）→ 第 3 节（FastAPI 与 .NET 生态对比）→ 第 4 节（目录结构）→ 第 7 节（日常开发循环）**；第 6 节与文首启动说明互补（User Secrets、环境清单），其余按需查阅。

---

## 2. 技术栈地图：每一块是干什么的

下面按「从外到内」说明本仓库用到的技术，以及**为什么常见选型会是它们**。

### 2.1 ASP.NET Core（Web 框架）

- **是什么**：微软开源的跨平台 Web 框架，用于接收 HTTP 请求、返回 JSON/文件等。
- **在本项目里**：提供 **Kestrel** 作为内置 Web 服务器；**控制器（Controller）** 对应 FastAPI 的「路由函数集合」；**中间件管道** 对应 Starlette/FastAPI 的中间件链。
- **版本**：本项目目标框架为 **.NET 9**（与「C# 13 / 运行时 9」配套）。安装 **[.NET 9 SDK](https://dotnet.microsoft.com/download)** 即可开发、运行。

### 2.2 控制器 + 路由（`Controllers/`）

- **是什么**：带有 `[ApiController]`、`[Route("...")]` 的类，里面的 public 方法通过 `[HttpGet]`、`[Post]` 等映射到 URL。
- **对照 FastAPI**：一个 `APIRouter` 往往对应这里的一个 `XXXController`；`prefix="/auth"` 对应 `[Route("auth")]` 放在类上。

### 2.3 依赖注入（DI，`Program.cs` 里的 `builder.Services.Add...`）

- **是什么**：由框架在运行时**自动创建对象并注入**到控制器构造函数里，而不是在控制器里手写 `new`。
- **对照 FastAPI**：类似 `Depends(get_session)`：声明「我要一个 `AppDbContext`」，框架按注册规则给你一个实例。
- **生命周期（常见三种）**：
  - **Singleton**：全进程一个实例（如 `RegionDataService` 包装 Redis 连接思路、邮件发送器若无状态也可考虑）。
  - **Scoped**：**每个 HTTP 请求**一个实例（**`AppDbContext` 必须是 Scoped**，避免多请求共用一个 DbContext 导致线程/并发问题）。
  - **Transient**：每次要的时候都 new（本项目中用得少）。

### 2.4 Entity Framework Core（EF Core）+ Pomelo（MySQL）

- **是什么**：**ORM（对象关系映射）**：用 C# 类（**实体 Entity**）表示表，用 **DbContext** 表示「当前与数据库的会话」，用 LINQ 写查询。
- **对照 Python**：`SQLAlchemy` 的 `Base` + `AsyncSession` + `select(Model)` 大致对应 `DbContext` + `DbSet<T>` + `db.XXX.Where(...)`。
- **Pomelo.EntityFrameworkCore.MySql**：EF Core 的 **MySQL 提供程序**，负责生成 MySQL 方言的 SQL、处理连接等。

### 2.5 JWT Bearer 认证

- **是什么**：无状态认证：服务端用密钥签名 Token，客户端在 `Authorization: Bearer <token>` 里带上；服务端验证签名与有效期。
- **在本项目里**：为与旧 Python **PyJWT** 兼容，载荷里仍使用 `iss` 存用户 id、`sub` 为 `"1"`（访问令牌）等约定；`Program.cs` 里配置 `AddAuthentication().AddJwtBearer(...)`。

### 2.6 其他类库（按功能）

| 包 | 作用 | 对照 Python |
|----|------|----------------|
| **BCrypt.Net-Next** | 密码哈希 | 原项目用 Argon2（不兼容，见文末说明） |
| **MailKit** | SMTP 发信 | `fastapi-mail` / `aiosmtplib` |
| **StackExchange.Redis** | Redis 客户端 | `redis.asyncio` |
| **ClosedXML** | 读写 Excel（xlsx） | `openpyxl` |
| **Swashbuckle.AspNetCore** | OpenAPI + Swagger UI | FastAPI 自带的 `/docs` |

---

## 3. FastAPI 与 ASP.NET Core 生态对比

本节在「能对应上」的基础上，补全**生态位**层面的对照：不单是某个 API 叫什么，而是**在整个后端工程里，各层通常由谁来做**。你已有 Python 基础时，可把 FastAPI 当作锚点，把 .NET 当作「同一角色的另一套实现」。

### 3.1 概念速查表（路由 / DI / 配置）

| Python / FastAPI | .NET / ASP.NET Core |
|------------------|---------------------|
| `app = FastAPI()` + `include_router` | `Program.cs` 里 `builder.Services` + `app.MapControllers()` |
| `Depends(get_session)` | 构造函数注入 `AppDbContext db` |
| Pydantic `BaseModel` | 控制器参数类型 + `Contracts/` 下的 DTO 类（也可用 record / 内联参数） |
| `response_model=` | `ActionResult<T>`、`ProducesResponseType` |
| `APIRouter(prefix="/auth")` | `[Route("auth")]` 在 Controller 类上 |
| `settings.py` / `os.getenv` | `appsettings.json` + `appsettings.{Environment}.json` + 环境变量 + User Secrets |
| Alembic 迁移 | `dotnet ef migrations` + `dotnet ef database update`（可选；也可沿用已有库） |
| Uvicorn / Hypercorn | **Kestrel**（`dotnet run` 内置；生产常配合 IIS、Nginx 反向代理、或容器） |

### 3.2 语言、运行时与工程单元

| 维度 | FastAPI（Python） | ASP.NET Core（.NET） |
|------|-------------------|---------------------|
| **语言** | Python（动态类型 + 类型提示） | C#（静态类型为主，可空引用、模式匹配） |
| **运行时** | CPython 解释执行；异步基于 `asyncio` | **CLR** + JIT；异步基于 `Task` / `async-await` |
| **可执行单元** | 一个目录 + `requirements.txt` / `pyproject.toml` | **`.csproj` 项目**（一个 Web 应用通常一个 csproj）；多个项目放在 **`.sln` 解决方案**里 |
| **依赖管理** | pip / Poetry / uv 等，包装在 PyPI | **NuGet**：包在 [nuget.org](https://www.nuget.org)，版本写在 `.csproj` 的 `<PackageReference>` |
| **锁文件** | 常见 `poetry.lock` / `uv.lock`（团队约定） | 可选 `packages.lock.json`；多数仓库以 `dotnet restore` 解析 csproj 为准 |

**学习提示**：在 Python 里你习惯「虚拟环境 + requirements」；在 .NET 里习惯改成「**SDK 版本 + csproj 里的包版本**」，全局工具用 `dotnet tool`。

### 3.3 Web 框架在生态中的位置

| 维度 | FastAPI | ASP.NET Core |
|------|---------|--------------|
| **定位** | 小型到中型 API 框架，构建在 **Starlette**（ASGI）上 | 全栈 Web 平台的一部分：API、Razor 页面、gRPC、SignalR 等**同一套主机模型** |
| **路由风格** | 函数 + 装饰器 `@app.get` / `APIRouter` | **Controller 类** + 特性 `[HttpGet]` 等（也可用 Minimal APIs 写函数式路由，本项目未用） |
| **中间件** | `app.middleware("http")` 等 | `app.Use...` 管道，顺序敏感（认证要在授权前等） |
| **内置 OpenAPI** | 默认生成 `/openapi.json`、`/docs` | 需 **Swashbuckle** 等包；本项目 Swagger UI 挂在 **`/docs`** 以对齐习惯 |

### 3.4 数据访问与「迁移」生态

| 维度 | FastAPI 常见组合 | ASP.NET Core 常见组合 |
|------|------------------|------------------------|
| **ORM** | SQLAlchemy 2.x（异步 `AsyncSession`） | **EF Core**（`DbContext`；异步 `SaveChangesAsync` / `ToListAsync`） |
| **驱动 / 方言** | `aiomysql`、驱动由 SQLAlchemy 适配 | **Pomelo**（MySQL）、Npgsql（PostgreSQL）、SqlServer 等 **Database Provider** |
| **迁移工具** | **Alembic**（与 SQLAlchemy 配合） | **`dotnet ef`**（与 EF Core 配合） |
| **模型定义** | `DeclarativeBase` + `Mapped` 列 | **POCO 类** + Fluent API（`OnModelCreating`）或数据注解 `[Table]` |

**对照理解**：Alembic 的 revision 链 ≈ EF 的 `Migrations` 文件夹里一串迁移类；二者都可「只维护模型、由工具生成 DDL」，也可像你本项目一样**沿用 Python 已建好的库**，只在 .NET 里把实体写对。

### 3.5 校验、序列化与错误返回

| 维度 | FastAPI | ASP.NET Core |
|------|---------|--------------|
| **入参校验** | Pydantic，自动 422 | **模型绑定** + **DataAnnotations**（`[Required]` 等）或 FluentValidation（本仓库以前者为主） |
| **JSON 命名** | 默认常为小驼峰或按 Pydantic 配置 | 本项目在 `Program.cs` 里设为 **`SnakeCaseLower`**，便于与 FastAPI 客户端对齐 |
| **典型错误形态** | `{"detail": ...}`（HTTPException） | `ProblemDetails` 或手写 `BadRequest(new { detail = ... })`（本项目部分接口刻意贴近 Python 的 `detail`） |

### 3.6 认证与安全相关生态

| 维度 | FastAPI 常见 | ASP.NET Core 常见 |
|------|--------------|-------------------|
| **JWT** | `python-jose` / PyJWT + 手写依赖 | **Microsoft.AspNetCore.Authentication.JwtBearer**，在 `Program.cs` 统一配置 |
| **密码哈希** | passlib / pwdlib（如 Argon2） | **ASP.NET Core Identity** 或独立库（本项目 **BCrypt.Net**） |
| **OAuth/OIDC** | 多用手写或第三方库 | 内置 **OpenIdConnect**、与 Azure AD 等集成文档齐全 |

### 3.7 异步与并发（重要差异）

| 维度 | FastAPI | ASP.NET Core |
|------|---------|--------------|
| **默认习惯** | 路由函数大量 `async def`，配合异步 DB/HTTP 客户端 | Controller **可以是同步方法**，也可 `async Task<IActionResult>`；**线程池**处理请求 |
| **Db 访问** | `AsyncSession` 全程 await | `DbContext` **非线程安全**，**每请求一个 Scoped 实例**，在 async action 里 `await ToListAsync()` |
| **阻塞调用** | 在 async 里阻塞会卡住事件循环 | 在 async 里长时间阻塞会占用线程池，仍建议 **await I/O**，重 CPU 用 `Task.Run` 等 |

**一句话**：两边都能写异步；Python 侧更要避免在 async 里调阻塞 IO；.NET 侧更要避免多个请求共用一个 `DbContext`。

### 3.8 横切能力（邮件、缓存、Excel、定时任务等）

| 能力 | Python / FastAPI 生态举例 | .NET 生态举例（本项目或常见） |
|------|---------------------------|-------------------------------|
| 邮件 | `fastapi-mail`、`aiosmtplib` | **MailKit** |
| Redis | `redis`、`redis.asyncio` | **StackExchange.Redis** |
| Excel | `openpyxl`、`pandas` | **ClosedXML**、EPPlus 等 |
| 后台任务 | `BackgroundTasks`、Celery、ARQ | `IHostedService`、`Hangfire`、Quartz.NET 等（本项目未引入） |

### 3.9 测试与质量（生态位对照）

| 维度 | Python | .NET |
|------|--------|------|
| 单元 / 集成测试 | `pytest`、`httpx.AsyncClient` + `TestClient` | **xUnit** / NUnit / MSTest，**WebApplicationFactory** 做集成测试 |
| 覆盖率 | `pytest-cov` | `coverlet`、dotnet test 集成 |

本项目为迁移示例，**未强制附带测试项目**；你学 .NET 时可下一步自建 `*.Tests` 项目练 `WebApplicationFactory`。

### 3.10 部署与主机（生态位对照）

| 维度 | FastAPI | ASP.NET Core |
|------|---------|--------------|
| 开发启动 | `uvicorn main:app --reload` | `dotnet watch run` / `dotnet run` |
| 生产进程 | Uvicorn + Gunicorn、Docker、K8s | **自托管 Kestrel**、**IIS**（Windows）、**Linux systemd**、Docker、K8s |
| 发布产物 | 代码 + venv / 镜像 | `dotnet publish` 输出可运行文件夹或单文件；常配合容器镜像 |

---

**小结**：第 2 节讲的是**本仓库里具体用了哪几个包**；第 3 节讲的是**在整条后端链路里，FastAPI 生态与 .NET 生态各自常见分工**。若你只记一张表，优先记 **3.1 + 3.4 + 3.7**（路由/DI、ORM+迁移、异步与 DbContext）。

---

## 4. 项目目录结构（建议对着资源管理器看一遍）

```
.net-ainame/
├── Zhiliao.Ainame.sln          # 解决方案入口
├── README.md
├── docs/
│   └── DEVELOPMENT.md          # 本文件
└── Zhiliao.Ainame.Api/
    ├── Program.cs              # 启动与 DI、中间件、认证、Swagger
    ├── Zhiliao.Ainame.Api.csproj   # 项目文件：目标框架、NuGet 包引用
    ├── appsettings.json        # 默认配置（勿提交真实密钥到公开仓库）
    ├── appsettings.Development.json  # 开发环境覆盖配置
    ├── Properties/
    │   └── launchSettings.json # 调试时监听的 URL、环境变量 ASPNETCORE_ENVIRONMENT
    ├── Controllers/            # HTTP 接口层（路由入口）
    ├── Data/
    │   └── AppDbContext.cs     # EF Core 数据库上下文 + Fluent 配置
    ├── Entities/               # 与表对应的实体类（ORM 模型）
    ├── Contracts/              # 请求/响应 DTO（数据契约）
    ├── Options/                # 强类型配置（Jwt、Smtp）
    └── Services/               # 可复用服务（JWT、邮件、Redis 省市区等）
```

**学习建议**：改一个接口时，路径一般是 **Controller →（需要时）Service → DbContext / Redis**；新增表时路径是 **Entity → AppDbContext → Controller**。

---

## 5. 一次 HTTP 请求在程序里怎么走（建立整体印象）

1. 浏览器或客户端发起请求，例如 `GET http://localhost:5027/school`。
2. **Kestrel** 接收连接，进入 **中间件管道**（顺序在 `Program.cs` 里：`UseAuthentication`、`UseAuthorization` 等）。
3. **路由**匹配到某个 `Controller` 的某个 action 方法。
4. 若该方法或类标了 `[Authorize]`，则 **JWT 中间件**会校验 Token，失败则直接 401，不会进入你的业务代码。
5. 框架 **构造控制器实例**，把已注册的依赖（如 `AppDbContext`）**注入构造函数**。
6. 你的 action 执行 LINQ / 调用 `SaveChangesAsync` 等，返回 `Ok(...)`、`NotFound()` 等，框架序列化为 **JSON**（本项目配置了 **snake_case** 命名策略，以贴近 FastAPI 默认 JSON 风格）。

---

## 6. 开发环境搭建与「从零跑通」步骤（建议按顺序做）

**说明**：**第一次启动请优先按文首《启动项目（具体操作）》逐步执行**；本节侧重「要装哪些软件」「User Secrets 完整示例」「数据库对表」等补充，避免与文首重复。

### 6.1 安装必备软件

1. 安装 **.NET 9 SDK**（命令行执行 `dotnet --version` 应显示 9.x）。
2. 安装并启动 **MySQL**，创建数据库 `zhiliao_ainame`（或沿用你 Python 项目已迁移好的库）。
3. 安装并启动 **Redis**（默认端口 6379），否则 `/region/*` 会报错。
4. 任选编辑器：**Visual Studio 2022**、**JetBrains Rider**、或 **VS Code + C# Dev Kit**。

### 6.2 克隆/打开代码后第一次运行

与文首《启动项目（具体操作）》**第 4～6 步相同**：在包含 `Zhiliao.Ainame.sln` 的根目录执行 `dotnet restore`、`dotnet build`、`dotnet run --project Zhiliao.Ainame.Api`，成功后访问 `http://localhost:5027/` 与 `http://localhost:5027/docs`。

### 6.3 配置数据库与密钥（重要）

**优先级（从高到低）**：环境变量 → User Secrets（仅开发）→ `appsettings.{Environment}.json` → `appsettings.json`。

1. 编辑 `Zhiliao.Ainame.Api/appsettings.Development.json`，把 `ConnectionStrings:DefaultConnection` 改成你的 MySQL 账号密码。
2. 修改 `Jwt:SecretKey` 为**足够长且随机**的字符串（生产环境绝不要用示例值）。
3. 若使用邮件与省市区：
   - 在 `Smtp` 中填 QQ 邮箱等 **SMTP 授权码**（不是登录密码）。
   - 确认 `Redis:ConnectionString` 指向正在运行的 Redis（默认 `127.0.0.1:6379`）。

**更安全的做法（推荐练习 User Secrets）**：在 `Zhiliao.Ainame.Api` 目录执行：

```bash
cd Zhiliao.Ainame.Api
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Server=127.0.0.1;Port=3306;Database=zhiliao_ainame;User=root;Password=你的密码;SslMode=None;CharSet=utf8mb4"
dotnet user-secrets set "Jwt:SecretKey" "这里写至少32字符的随机串"
dotnet user-secrets set "Smtp:UserName" "你的发件邮箱"
dotnet user-secrets set "Smtp:Password" "SMTP授权码"
dotnet user-secrets set "Redis:ConnectionString" "127.0.0.1:6379"
```

User Secrets 存储在用户目录，**不会提交到 Git**，适合本地学习。

### 6.4 验证数据库是否「对得上」

若表结构与 Python Alembic 一致，**无需**先执行 EF 迁移即可读写。若启动后出现「表不存在」等错误：

- 要么在 MySQL 里执行 Python 侧已有迁移；
- 要么学习使用 `dotnet ef` 生成迁移（进阶，见第 9 节）。

---

## 7. 日常开发循环（你以后会反复做这些事）

1. **改代码**：通常从 `Controllers/` 或 `Services/` 开始。
2. **编译检查**：`dotnet build`（或在 IDE 里保存即编译）。
3. **运行**：`dotnet run --project Zhiliao.Ainame.Api`，或 IDE 里 F5。
4. **调试接口**：浏览器打开 `/docs`，或用 VS Code REST Client / `Zhiliao.Ainame.Api.http`（若存在）。
5. **看日志**：控制台输出；需要更细时在 `appsettings.Development.json` 里把 `Logging:LogLevel:Default` 设为 `Debug`。

**加一个新接口的推荐步骤**（练习用）：

1. 若涉及新表：在 `Entities/` 加类 → 在 `AppDbContext` 里 `DbSet` + `OnModelCreating` 配置关系/索引。
2. 在 `Contracts/` 加请求/响应 DTO（若有）。
3. 在 `Controllers/` 加 action，注入 `AppDbContext`。
4. `dotnet build` → `dotnet run` → `/docs` 里点「Try it out」测试。

---

## 8. 调试方式详解

### 8.1 Visual Studio / Rider

1. 用 IDE 打开 `Zhiliao.Ainame.sln`。
2. 将启动项目设为 `Zhiliao.Ainame.Api`。
3. 在控制器行号左侧**打断点**，按 **F5**。
4. 用 Swagger 或 Postman 发请求，命中断点后可在「局部变量」窗口查看 `db`、`User` 等。

### 8.2 VS Code

1. 安装 **C# Dev Kit**。
2. 打开文件夹 `.net-ainame`。
3. 生成/编辑 `.vscode/launch.json`，类型选 **.NET**，program 指向编译出的 `Zhiliao.Ainame.Api.dll` 或使用「动态生成」模板。
4. F5 启动调试。

### 8.3 附加到进程

先命令行 `dotnet run`，再在 IDE 里选择「附加到进程」，选中 `Zhiliao.Ainame.Api` 进程。适合已启动服务、只想临时调试的场景。

---

## 9. 数据库与 EF Core（学习要点）

### 9.1 DbContext 是什么

`AppDbContext` 继承 `DbContext`，里面的 `DbSet<实体>` 大致对应一张表。每次请求注入的 `AppDbContext` 是 **Scoped**，**不要在 Singleton 服务里长期持有 DbContext**。

### 9.2 常用操作与 SQLAlchemy 对照

| 意图 | EF Core（异步） |
|------|------------------|
| 查询 | `await db.Schools.Where(...).ToListAsync()` |
| 新增 | `db.Schools.Add(entity); await db.SaveChangesAsync()` |
| 更新 | 先 `FirstOrDefaultAsync` 取出，改属性，再 `SaveChangesAsync` |
| 批量删除（EF7+） | `await db.Table.Where(...).ExecuteDeleteAsync()` |

### 9.3 迁移（进阶）

若要从零建库，可学习：

```bash
dotnet tool install -g dotnet-ef
cd Zhiliao.Ainame.Api
dotnet ef migrations add InitialCreate -o Data/Migrations
dotnet ef database update
```

**注意**：若数据库已由 Python 创建，迁移可能与现有表冲突，需先比对实体与真实表结构，或只把迁移当作学习练习在空库上演示。

---

## 10. 配置系统（读配置代码时对照看）

- **`appsettings.json`**：默认配置，常提交到 Git（不含机密）。
- **`appsettings.Development.json`**：当 `ASPNETCORE_ENVIRONMENT=Development` 时**覆盖**上一项（本地调试默认就是 Development）。
- **环境变量**：例如 `ConnectionStrings__DefaultConnection`（双下划线表示嵌套键），适合容器与生产。
- **User Secrets**：开发机上的密钥存储，通过 `dotnet user-secrets` 管理。

在代码里读配置：`builder.Configuration["Jwt:SecretKey"]` 或 `builder.Services.Configure<JwtOptions>(...)` 绑定到 `Options` 类（见 `Options/JwtOptions.cs`）。

---

## 11. 认证与授权在本项目中的行为

- **登录**：`POST /auth/login` 返回 `token`（访问令牌）。
- **携带方式**：请求头 `Authorization: Bearer <token>`。
- **保护接口**：在 action 或整个 Controller 上标 `[Authorize]`（例如 `POST /admin/queryArt`）。
- **Swagger 里试 JWT**：`/docs` 右上角 **Authorize**，输入 `Bearer xxx`。

`Program.cs` 里 `JwtBearerEvents.OnTokenValidated` 中校验 `sub == "1"`，是为了与旧 Python 对「访问令牌」类型的约定一致。

---

## 12. 常用 `dotnet` 命令速查

| 命令 | 作用 |
|------|------|
| `dotnet restore` | 根据 csproj 下载 NuGet 包 |
| `dotnet build` | 编译 |
| `dotnet run --project Zhiliao.Ainame.Api` | 编译并运行 Web 项目 |
| `dotnet watch run --project Zhiliao.Ainame.Api` | 文件变更自动重启（适合练手） |
| `dotnet clean` | 清理生成输出 |

---

## 13. 故障排查清单

| 现象 | 可能原因 | 建议 |
|------|-----------|------|
| 启动即异常：连接字符串 | MySQL 未启动或库名/密码错误 | 检查 `DefaultConnection`，用客户端工具试连 |
| `/region/*` 报错 | Redis 未启动或未配置 | 启动 Redis，检查 `Redis:ConnectionString` |
| 401 on `[Authorize]` | 未带 Token 或过期、密钥不一致 | 重新登录；开发与生产 `Jwt:SecretKey` 必须一致才能验旧 Token |
| 表不存在 | 库空或表名不一致 | 用 Python 迁移建表，或学习 `dotnet ef` |
| Swagger 打不开 | 非 Development 环境默认不启用 | 设 `ASPNETCORE_ENVIRONMENT=Development`，或改 `Program.cs`（不推荐生产开启） |

---

## 14. 与 Python 版本的已知差异（学习时心里有数）

- **密码**：本仓库用 **BCrypt**；原 Python 用 **Argon2**。同一数据库里旧用户密码哈希无法直接用 .NET 登录验证，需**重置密码或重新注册**。
- **Excel**：ClosedXML 主要针对 **xlsx**；若必须用旧版 `.xls`，需另选组件或先转换格式。
- **公司删除**：.NET 实现会清理关联订单及明细，避免外键/孤儿数据问题；与 Python 原仓库「只删部分关联」的行为可能略有不同，属于**更稳妥**的实现。

---

## 15. 官方文档与延伸学习（权威入口）

按推荐顺序阅读微软文档（均为英文为主，可浏览器翻译）：

1. [ASP.NET Core 概述](https://learn.microsoft.com/aspnet/core/fundamentals/)
2. [Web API 教程](https://learn.microsoft.com/aspnet/core/tutorials/first-web-api)
3. [Entity Framework Core 概述](https://learn.microsoft.com/ef/core/)
4. [依赖注入](https://learn.microsoft.com/aspnet/core/fundamentals/dependency-injection)
5. [配置](https://learn.microsoft.com/aspnet/core/fundamentals/configuration/)

---

## 附录 A：完整路由表（与 `zhiliao-ainame/main.py` 对齐）

JSON 默认 **snake_case**（在 `Program.cs` 的 `AddJsonOptions` 中配置）。

### 通用

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 欢迎 |
| GET | `/hello/{name}` | 问候 |
| GET | `/mail/test?email=` | 邮件测试 |

### 认证 / 起名

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/auth/code?email=` | 邮箱验证码 |
| POST | `/auth/register` | 注册 |
| POST | `/auth/login` | 登录 |
| POST | `/name` | 起名（占位） |

### 文章管理（`/admin`）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/admin/insertArt` | multipart 上传 |
| POST | `/admin/delArt` | 批量删除，返回条数 |
| POST | `/admin/changeArt` | 修改 |
| POST | `/admin/queryArt` | 查询（**需 JWT**） |
| POST | `/admin/queryArtOut` | 查询（`code/message/data`） |
| POST | `/admin/queryArtExcel` | 导出 xlsx |
| POST | `/admin/insertArtByExcel` | 导入 xlsx |

### 省市区（Redis）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/region/provinces` | 省份 |
| GET | `/region/cities?province_code=` | 城市 |
| GET | `/region/districts?city_code=` | 区县 |
| POST | `/region/init` | 初始化示例数据 |

### 校园

| 前缀 | 说明 |
|------|------|
| `/school` | 学校 CRUD |
| `/teacher` | 班主任 CRUD；`?school_id=` |
| `/student` | 学生 CRUD；`?teacher_id=`；含选课与分数 |
| `/course` | 课程 CRUD |
| `/student-course` | 批量/单条选课、筛选、按课程查学生等 |

### 订单模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/company/create` | 创建公司 |
| GET | `/company/query` | 查询公司 |
| PUT | `/company/update` | 更新 |
| DELETE | `/company/delete?company_id=` | 删除 |
| POST | `/product/create` | 创建产品 |
| GET | `/product/query` | 查询产品 |
| PUT | `/product/update` | 更新 |
| DELETE | `/product/delete?prduct_id=` | 删除（参数名与 Python 一致） |
| POST | `/order/create` | 创建订单 |
| PUT | `/order/update` | 更新订单 |
| GET | `/order/query` | 查询（`msg` 字段） |
| DELETE | `/order/delete?id=` | 删除订单 |

---

**结语**：先把 **第 6 节跑通**，再在 **第 7 节**里自己改一个小接口（例如改 `/` 的返回文案），配合断点走一遍请求链路，你会对 ASP.NET Core 的「入口 → DI → Controller → DbContext」有非常具体的认识。遇到新概念，回到 **第 2～3 节**查表，并用 **第 15 节**官方文档加深理解即可。
