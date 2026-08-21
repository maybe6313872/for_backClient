// =============================================================================
// Program.cs — ASP.NET Core 应用入口（最小宿主模型 / Top-level statements）
// -----------------------------------------------------------------------------
// 阅读顺序建议：
//   1) WebApplication.CreateBuilder：收集配置、注册「服务」到 DI 容器
//   2) builder.Build()：生成 WebApplication
//   3) app.Use* / app.Map*：配置「中间件管道」与终结点
//   4) app.Run()：启动 Kestrel 监听端口
// 对照 FastAPI：AddDbContext ≈ 依赖注入 get_db；AddControllers ≈ 注册路由；
// UseAuthentication/Authorization ≈ 依赖里校验 JWT 的全局前置逻辑。
// =============================================================================

using System.IdentityModel.Tokens.Jwt;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using Pomelo.EntityFrameworkCore.MySql;
using StackExchange.Redis;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Options;
using Zhiliao.Ainame.Api.Services;

// JWT 库默认会把 claim 名映射成冗长 URI；清掉后 Token 里仍用短名 iss/sub（与 Python PyJWT 一致）
JwtSecurityTokenHandler.DefaultInboundClaimTypeMap.Clear();

var builder = WebApplication.CreateBuilder(args);

// ----- 配置绑定到强类型 Options（对应 appsettings.json 里的 Jwt、Smtp 节点）-----
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection(JwtOptions.SectionName));
builder.Services.Configure<SmtpOptions>(builder.Configuration.GetSection(SmtpOptions.SectionName));

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? throw new InvalidOperationException("未配置连接字符串 ConnectionStrings:DefaultConnection。");

// ----- EF Core + Pomelo：每个 HTTP 请求一个 Scoped DbContext，用完释放 -----
builder.Services.AddDbContext<AppDbContext>(options =>
{
    // AutoDetect：首次连库时探测 MySQL 版本，生成兼容的 SQL 方言
    var serverVersion = ServerVersion.AutoDetect(connectionString);
    options.UseMySql(connectionString, serverVersion);
});

builder.Services.AddScoped<IJwtTokenService, JwtTokenService>();
// 发邮件无会话状态，用 Singleton 即可（内部每次 Send 会新建 SmtpClient）
builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();

// RegionDataService 需要 Redis：连接串为空时不连 Redis，访问 /region 时再抛清晰错误
builder.Services.AddSingleton(sp =>
{
    var cs = sp.GetRequiredService<IConfiguration>()["Redis:ConnectionString"];
    IConnectionMultiplexer? mux = string.IsNullOrWhiteSpace(cs) ? null : ConnectionMultiplexer.Connect(cs);
    return new RegionDataService(mux);
});

var jwtKey = builder.Configuration["Jwt:SecretKey"]
    ?? throw new InvalidOperationException("未配置 Jwt:SecretKey。");
var signingKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey));

// ----- 认证：Bearer JWT；与 Python 一样用对称密钥 HMAC-SHA256 签发/验签 -----
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = signingKey,
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(1)
        };
        // Token 校验通过后额外业务规则：sub 必须为 "1" 表示访问令牌（刷新令牌为 "2"）
        options.Events = new JwtBearerEvents
        {
            OnTokenValidated = context =>
            {
                var sub = context.Principal?.FindFirst("sub")?.Value;
                if (sub != "1")
                    context.Fail("Token类型错误！");
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddAuthorization();

// ----- 控制器 + JSON：snake_case 输出，贴近 FastAPI 默认 pydantic 序列化风格 -----
builder.Services.AddControllers()
    .AddJsonOptions(o =>
    {
        o.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower;
        o.JsonSerializerOptions.DictionaryKeyPolicy = JsonNamingPolicy.SnakeCaseLower;
    });

// OpenAPI 元数据 + Swagger UI（仅 Development 下启用，见下方）
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "知了AI起名 API",
        Version = "1.0.0",
        Description = "ASP.NET Core 版后端，完整迁移原 FastAPI（zhiliao-ainame）路由：认证、起名、文章/Excel、省市区(Redis)、校园、订单等。"
    });
    // 在 Swagger UI 里点 Authorize，输入 Bearer {token} 即可带 JWT 调受保护接口
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "Authorization: Bearer {token}",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT"
    });
    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "Bearer" }
            },
            Array.Empty<string>()
        }
    });
});

var app = builder.Build();

// 开发环境：暴露 Swagger JSON 与 UI；RoutePrefix = docs → 浏览器 /docs
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "知了AI起名 v1");
        c.RoutePrefix = "docs";
    });
}

// 生产环境才强制 HTTPS 重定向，本地 http 调试更省事
if (!app.Environment.IsDevelopment())
    app.UseHttpsRedirection();

// 顺序重要：先认证（解析 JWT）再授权（检查 [Authorize]）
app.UseAuthentication();
app.UseAuthorization();
// 根据 Controller 上的 [Route]、[HttpGet] 等注册终结点；未匹配的 URL 返回 404
app.MapControllers();
// 阻塞当前线程，启动 Kestrel 监听；Ctrl+C 触发优雅关闭
app.Run();
