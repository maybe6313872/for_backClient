# C#语法应用

本文面向有 JavaScript / 前端经验的开发者，用 JS 心智模型对照理解本项目里的 C# 和 .NET 写法。

阅读建议：先把 C# 当成“更严格、更显式的 TypeScript + 后端框架工程体系”来看。很多概念并不陌生，只是名字和组织方式变了。

## 1. 项目与依赖管理

| JS / Node | C# / .NET | 说明 |
|---|---|---|
| `package.json` | `.csproj` | 项目配置文件，声明目标框架、依赖包、构建设置。 |
| `npm install` | `dotnet restore` | 根据项目文件还原依赖。 |
| `npm run dev` | `dotnet watch run` | 开发模式运行，文件变化后自动重新编译/重启。 |
| `npm run build` | `dotnet build` | 编译项目。 |
| `node_modules` | NuGet 缓存 + `obj/` + `bin/` | .NET 不把依赖集中放在项目内的 `node_modules`，而是全局缓存包，并在构建时生成中间文件和输出 DLL。 |
| npmjs.com | nuget.org | .NET 公共包仓库。 |

常见命令：

```powershell
dotnet restore
dotnet build
dotnet run --project .\Zhiliao.Ainame.Api\Zhiliao.Ainame.Api.csproj
dotnet watch run --project .\Zhiliao.Ainame.Api\Zhiliao.Ainame.Api.csproj
```

安装第三方包：

```powershell
dotnet add .\Zhiliao.Ainame.Api\Zhiliao.Ainame.Api.csproj package Newtonsoft.Json
```

`.csproj` 里会出现：

```xml
<PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
```

## 2. `using` 与 `import`

JS：

```js
import { JsonConvert } from "some-package";
```

C#：

```csharp
using Newtonsoft.Json;
```

二者相似，但不是完全一样。

`using` 不是“从某个文件导入某个变量”，而是“告诉编译器：当前文件里可以使用这个命名空间下的类型短名”。

比如：

```csharp
using System.IdentityModel.Tokens.Jwt;

JwtSecurityTokenHandler.DefaultInboundClaimTypeMap.Clear();
```

等价于写完整名字：

```csharp
System.IdentityModel.Tokens.Jwt.JwtSecurityTokenHandler
    .DefaultInboundClaimTypeMap
    .Clear();
```

重点：

```text
.csproj / ProjectReference / PackageReference 决定项目能看到哪些代码和 DLL
using 只是让当前文件能用更短的类型名
```

## 3. `namespace` 与模块路径

JS 通常通过文件路径组织模块：

```js
import { User } from "./entities/User";
```

C# 通过 `namespace` 组织类型：

```csharp
namespace Zhiliao.Ainame.Api.Entities;

public class AppUser
{
}
```

别的文件使用：

```csharp
using Zhiliao.Ainame.Api.Entities;

var user = new AppUser();
```

也可以不用 `using`，直接写完整名：

```csharp
var user = new Zhiliao.Ainame.Api.Entities.AppUser();
```

注意：`namespace` 不是文件路径。只是大家通常会让目录结构和 namespace 对齐，便于阅读。

例如：

```text
Entities/AppUser.cs
```

通常写：

```csharp
namespace Zhiliao.Ainame.Api.Entities;
```

## 4. 同名类型冲突怎么办

如果两个命名空间里都有 `User`：

```csharp
using MyApp.Entities;
using ThirdParty.Auth;

var user = new User(); // 编译器不知道是哪一个 User
```

可以写完整名：

```csharp
var appUser = new MyApp.Entities.User();
var authUser = new ThirdParty.Auth.User();
```

也可以起别名：

```csharp
using AppUser = MyApp.Entities.User;
using AuthUser = ThirdParty.Auth.User;

var appUser = new AppUser();
var authUser = new AuthUser();
```

类似 JS：

```js
import { User as AppUser } from "./entities";
import { User as AuthUser } from "third-party-auth";
```

## 5. 本地类、跨项目库、第三方包

### 同一个项目内

只要 `.cs` 文件在同一个 `.csproj` 项目目录内，SDK 风格项目默认会自动参与编译。

```csharp
namespace Zhiliao.Ainame.Api.Services;

public class MyNameService
{
    public string Generate()
    {
        return "张三";
    }
}
```

别的文件：

```csharp
using Zhiliao.Ainame.Api.Services;

var service = new MyNameService();
```

不需要手动 export，也不需要单独编译这个文件。最终 `dotnet build` 时整个项目一起编译。

### 跨项目使用

结构：

```text
.net-ainame/
├── Zhiliao.Ainame.Api/
│   └── Zhiliao.Ainame.Api.csproj
└── Zhiliao.Ainame.Common/
    └── Zhiliao.Ainame.Common.csproj
```

在 API 项目里添加：

```xml
<ItemGroup>
  <ProjectReference Include="..\Zhiliao.Ainame.Common\Zhiliao.Ainame.Common.csproj" />
</ItemGroup>
```

或者用命令：

```powershell
dotnet add .\Zhiliao.Ainame.Api\Zhiliao.Ainame.Api.csproj reference .\Zhiliao.Ainame.Common\Zhiliao.Ainame.Common.csproj
```

然后代码里：

```csharp
using Zhiliao.Ainame.Common;
```

### 第三方包

`.csproj`：

```xml
<PackageReference Include="MailKit" Version="4.15.1" />
```

代码：

```csharp
using MailKit.Net.Smtp;
```

注意：包名不一定等于 namespace 名。实际 `using` 什么，要看这个包暴露了哪些公开类型。

## 6. `public`、`internal` 与可见性

JS/TS 常见：

```ts
export class UserService {}
```

C#：

```csharp
public class UserService
{
}
```

常见访问修饰符：

| C# | 类比理解 | 作用 |
|---|---|---|
| `public` | `export` | 其他项目也可以访问。 |
| `internal` | 包内可见 | 当前项目/程序集内部可访问，跨项目不可访问。 |
| `private` | 私有 | 只在当前类内部可访问。 |
| `protected` | 继承可见 | 当前类和子类可访问。 |

如果类前面什么都不写：

```csharp
class MyService
{
}
```

顶级类默认是 `internal`，同项目能用，跨项目不能用。

## 7. 类、对象、静态成员

JS：

```js
class UserService {
  generate() {}

  static version = "1.0";
}

const service = new UserService();
service.generate();
UserService.version;
```

C#：

```csharp
public class UserService
{
    public string Generate()
    {
        return "ok";
    }

    public static string Version = "1.0";
}

var service = new UserService();
service.Generate();
UserService.Version;
```

本项目里：

```csharp
JwtSecurityTokenHandler.DefaultInboundClaimTypeMap.Clear();
```

这里没有 `new JwtSecurityTokenHandler()`，因为访问的是静态成员，类似：

```ts
SomeClass.staticProperty
```

## 8. `var` 与类型推断

JS：

```js
const name = "Tom";
```

C#：

```csharp
var name = "Tom";
```

C# 的 `var` 不是动态类型。编译器会在编译时推断出类型。

```csharp
var count = 1;       // int
var text = "hello";  // string
```

推断后类型就固定了：

```csharp
var count = 1;
count = "hello"; // 编译错误
```

如果想显式写类型：

```csharp
int count = 1;
string text = "hello";
```

## 9. 可空类型与 `?`

TypeScript：

```ts
let name: string | null = null;
```

C#：

```csharp
string? name = null;
```

普通 `string` 表示不希望为 null：

```csharp
string name = "Tom";
```

`int?` 表示可空数字：

```csharp
int? age = null;
```

本项目 DTO 里常见：

```csharp
public string? Other { get; set; }
public int? SchoolId { get; set; }
```

这通常表示前端可以不传这个字段，或者传 `null`。

## 10. 属性：`get; set;`

JS：

```js
const user = {
  email: "",
  username: ""
};
```

C# DTO / Entity 常见：

```csharp
public class UserDto
{
    public int Id { get; set; }
    public string Email { get; set; } = "";
    public string Username { get; set; } = "";
}
```

`get; set;` 表示这是一个可读可写属性。

```csharp
var user = new UserDto();
user.Email = "a@test.com";
Console.WriteLine(user.Email);
```

`= ""` 是默认值，避免非空字符串初始为 null。

## 11. 方法、返回类型与 `Task`

JS：

```js
async function login(data) {
  return result;
}
```

C#：

```csharp
public async Task<LoginResponse> Login(LoginRequest data)
{
    return result;
}
```

常见返回类型：

| C# | 含义 |
|---|---|
| `void` | 不返回值。 |
| `string` / `int` / 自定义类 | 同步返回具体类型。 |
| `Task` | 异步操作，不返回结果。 |
| `Task<T>` | 异步操作，返回 `T`。 |
| `ActionResult<T>` | Web API 返回结果，可返回 `Ok(T)`、`BadRequest(...)`、`NotFound(...)` 等。 |

本项目里：

```csharp
public async Task<ActionResult<LoginResponse>> Login(...)
```

含义是：这是一个异步接口方法，成功时通常返回 `LoginResponse`，也可能返回 400/500 等 HTTP 响应。

## 12. `async` / `await`

JS：

```js
const user = await db.users.findOne();
```

C#：

```csharp
var user = await db.Users.FirstOrDefaultAsync();
```

很像，但 C# 的异步返回类型通常是 `Task` 或 `Task<T>`。

本项目常见：

```csharp
await db.SaveChangesAsync(ct).ConfigureAwait(false);
```

可以先粗略理解为：

```text
await db.SaveChangesAsync(ct)
```

`.ConfigureAwait(false)` 是库/后端代码里常见的异步上下文优化写法，学习初期不必纠结。

## 13. Controller 与路由

FastAPI / Express 思维：

```js
app.get("/hello/:name", (req, res) => {});
```

C# Controller：

```csharp
[ApiController]
[Route("auth")]
public class AuthController : ControllerBase
{
    [HttpPost("login")]
    public async Task<ActionResult<LoginResponse>> Login(...)
    {
    }
}
```

组合后路径是：

```text
POST /auth/login
```

常见特性：

| C# 特性 | 作用 |
|---|---|
| `[ApiController]` | 声明这是 Web API Controller，并启用自动模型校验等行为。 |
| `[Route("auth")]` | 类级路由前缀。 |
| `[HttpGet("code")]` | GET 路由。 |
| `[HttpPost("login")]` | POST 路由。 |
| `[FromBody]` | 从 JSON body 绑定参数。 |
| `[FromQuery]` | 从 query string 绑定参数。 |
| `[Authorize]` | 需要认证 token。 |

## 14. 依赖注入：构造函数参数从哪里来

JS 里可能手动创建：

```js
const db = createDb();
const controller = new AuthController(db, emailSender, jwt);
```

C# ASP.NET Core 常见：

```csharp
public class AuthController(
    AppDbContext db,
    IEmailSender emailSender,
    IJwtTokenService jwt) : ControllerBase
{
}
```

这叫构造函数注入。对象由框架创建，参数从 DI 容器里拿。

注册位置在 `Program.cs`：

```csharp
builder.Services.AddDbContext<AppDbContext>(...);
builder.Services.AddScoped<IJwtTokenService, JwtTokenService>();
builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();
```

类比：

```text
先在容器里注册服务
请求进来时框架创建 Controller
构造函数需要什么，框架就注入什么
```

## 15. Interface 与实现类

TypeScript：

```ts
interface EmailSender {
  sendPlain(to: string, subject: string, body: string): Promise<void>;
}
```

C#：

```csharp
public interface IEmailSender
{
    Task SendPlainAsync(string to, string subject, string body, CancellationToken cancellationToken = default);
}
```

实现：

```csharp
public class SmtpEmailSender : IEmailSender
{
    public Task SendPlainAsync(string to, string subject, string body, CancellationToken cancellationToken = default)
    {
        // SMTP 发信
    }
}
```

注册：

```csharp
builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();
```

意思是：代码里要 `IEmailSender` 时，实际给 `SmtpEmailSender`。

## 16. Entity、DTO、DbContext

在前端项目里，你可能会区分：

```text
后端表结构
接口入参
接口返回值
页面展示模型
```

在本项目里对应：

| 概念 | 项目目录 | 作用 |
|---|---|---|
| Entity | `Entities/` | 数据库表映射类。 |
| DTO / Contract | `Contracts/` | API 请求/响应的数据形状。 |
| DbContext | `Data/AppDbContext.cs` | EF Core 数据库会话，负责查询、保存、表关系配置。 |
| Controller | `Controllers/` | HTTP 接口入口。 |
| Service | `Services/` | 可复用业务能力，如发邮件、JWT、省市区 Redis。 |

Entity 示例：

```csharp
public class AppUser
{
    public int Id { get; set; }
    public string Email { get; set; } = "";
    public string PasswordHash { get; set; } = "";
}
```

DTO 示例：

```csharp
public class LoginRequest
{
    public string Email { get; set; } = "";
    public string Password { get; set; } = "";
}
```

Controller 使用：

```csharp
var user = await db.Users.FirstOrDefaultAsync(u => u.Email == data.Email, ct);
```

## 17. LINQ：C# 里的查询表达

JS：

```js
const users = list
  .filter(x => x.age > 18)
  .map(x => x.name);
```

C#：

```csharp
var names = users
    .Where(x => x.Age > 18)
    .Select(x => x.Name)
    .ToList();
```

EF Core 里：

```csharp
var user = await db.Users
    .Where(u => u.Email == data.Email)
    .FirstOrDefaultAsync(ct);
```

这不只是内存数组操作。对 `DbSet<T>` 使用 LINQ 时，EF Core 会把它翻译成 SQL。

## 18. JSON 字段命名

JS/前端常用：

```json
{
  "user_name": "Tom"
}
```

C# 属性通常是 PascalCase：

```csharp
public string UserName { get; set; } = "";
```

本项目在 `Program.cs` 里配置了 snake_case：

```csharp
o.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
```

所以 C#：

```csharp
UserName
```

输出 JSON 时会变成：

```json
{
  "user_name": "Tom"
}
```

## 19. `new()`、对象初始化器

JS：

```js
const user = {
  email: "a@test.com",
  username: "Tom"
};
```

C#：

```csharp
var user = new AppUser
{
    Email = "a@test.com",
    Username = "Tom"
};
```

如果类型能从左边推断，也可以：

```csharp
AppUser user = new()
{
    Email = "a@test.com",
    Username = "Tom"
};
```

## 20. `List<T>` 与数组/集合

JS：

```js
const ids = [1, 2, 3];
ids.push(4);
```

C#：

```csharp
var ids = new List<int> { 1, 2, 3 };
ids.Add(4);
```

本项目使用了 C# 新语法：

```csharp
public List<string> Exclude { get; set; } = [];
```

这里的 `[]` 是集合表达式，等价于创建一个空列表。

## 21. Attribute：方括号元数据

C# 里经常看到：

```csharp
[Required]
[MaxLength(100)]
public string Email { get; set; } = "";
```

这些叫 Attribute，可以理解为“贴在类、方法、属性上的元数据”。

在 Web API 中常见用途：

```text
[Required]       入参必填校验
[MaxLength(100)] 最大长度校验
[Route("auth")]  路由配置
[HttpPost]       HTTP 方法配置
[Authorize]      鉴权要求
```

有点像前端框架里的装饰器：

```ts
@Controller()
@Post()
```

## 22. 看本项目代码时的最短路径

建议按这个顺序读：

```text
Zhiliao.Ainame.Api.csproj
    ↓
Program.cs
    ↓
Controllers/RootController.cs
    ↓
Controllers/AuthController.cs
    ↓
Contracts/ApiDtos.cs
    ↓
Entities/AppUser.cs
    ↓
Data/AppDbContext.cs
    ↓
Services/JwtTokenService.cs
```

这条线能串起：

```text
项目依赖
启动配置
HTTP 路由
请求/响应 DTO
数据库实体
EF Core 查询
JWT 服务
依赖注入
```

也就是 ASP.NET Core Web API 的主干。

