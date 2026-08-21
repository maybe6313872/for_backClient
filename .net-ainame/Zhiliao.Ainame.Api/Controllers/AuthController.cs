using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;
using Zhiliao.Ainame.Api.Services;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 认证相关：<c>/auth/code</c> 发验证码、<c>/auth/register</c> 注册、<c>/auth/login</c> 登录。
/// <para>通过主构造函数注入 <see cref="AppDbContext"/>、<see cref="IEmailSender"/>、<see cref="IJwtTokenService"/>（.NET 8+ 语法）。</para>
/// </summary>
[ApiController]
[Route("auth")]
public class AuthController(
    AppDbContext db,
    IEmailSender emailSender,
    IJwtTokenService jwt) : ControllerBase
{
    /// <summary>
    /// <c>GET /auth/code?email=</c>：生成 4 位数字，发邮件，并写入 <see cref="EmailCode"/> 表。
    /// <para>邮件文案写「五分钟有效」，数据库校验窗口为 10 分钟（与 Python 一致）。</para>
    /// </summary>
    [HttpGet("code")]
    [ProducesResponseType(typeof(ResponseOut), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ResponseOut>> GetEmailCode([FromQuery] string email, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(email))
            return BadRequest(new { detail = "邮箱不能为空" });

        var code = Random.Shared.Next(0, 10000).ToString("D4");
        const string subject = "【知了课堂】注册验证码";
        var body = $"您的验证码为：{code}，五分钟有效！";

        try
        {
            await emailSender.SendPlainAsync(email, subject, body, ct).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"邮件发送失败：{ex.Message}" });
        }

        db.EmailCodes.Add(new EmailCode
        {
            Email = email,
            Code = code,
            CreatedTime = DateTime.Now,
            Type = "test"
        });
        await db.SaveChangesAsync(ct).ConfigureAwait(false);
        return Ok(new ResponseOut());
    }

    /// <summary><c>POST /auth/register</c>：校验验证码、邮箱唯一性，BCrypt 哈希密码后插入用户。</summary>
    [HttpPost("register")]
    [ProducesResponseType(typeof(ResponseOut), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<ResponseOut>> Register([FromBody] RegisterRequest data, CancellationToken ct)
    {
        var emailExists = await db.Users.AnyAsync(u => u.Email == data.Email, ct).ConfigureAwait(false);
        if (emailExists)
            return BadRequest(new { detail = "该邮箱已经存在！" });

        if (!await IsEmailCodeValidAsync(data.Email, data.Code, ct).ConfigureAwait(false))
            return BadRequest(new { detail = "邮箱或验证码错误！" });

        var hash = BCrypt.Net.BCrypt.HashPassword(data.Password);
        db.Users.Add(new AppUser
        {
            Email = data.Email,
            Username = data.Username,
            PasswordHash = hash
        });

        try
        {
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }

        return Ok(new ResponseOut());
    }

    /// <summary><c>POST /auth/login</c>：返回 <c>token</c> 供 Swagger Authorize 或 <c>Authorization: Bearer</c>。</summary>
    [HttpPost("login")]
    [ProducesResponseType(typeof(LoginResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<LoginResponse>> Login([FromBody] LoginRequest data, CancellationToken ct)
    {
        var user = await db.Users.FirstOrDefaultAsync(u => u.Email == data.Email, ct).ConfigureAwait(false);
        if (user is null)
            return BadRequest(new { detail = "该用户不存在！" });

        var ok = BCrypt.Net.BCrypt.Verify(data.Password, user.PasswordHash);
        if (!ok)
            return BadRequest(new { detail = "邮箱或密码错误！" });

        // 与 Python 对齐：响应里 token 字段为访问令牌；刷新令牌已生成但未单独返回
        var (access, _) = jwt.CreateLoginTokens(user.Id);
        return Ok(new LoginResponse
        {
            User = new UserDto { Id = user.Id, Email = user.Email, Username = user.Username },
            Token = access
        });
    }

    /// <summary>取该邮箱最新一条验证码，匹配且创建时间在 10 分钟内则有效。</summary>
    private async Task<bool> IsEmailCodeValidAsync(string email, string code, CancellationToken ct)
    {
        var row = await db.EmailCodes
            .Where(e => e.Email == email && e.Code == code)
            .OrderByDescending(e => e.Id)
            .FirstOrDefaultAsync(ct)
            .ConfigureAwait(false);
        if (row is null)
            return false;
        return (DateTime.Now - row.CreatedTime) <= TimeSpan.FromMinutes(10);
    }
}
