using Microsoft.AspNetCore.Mvc;
using Zhiliao.Ainame.Api.Services;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 根路径与健康/邮件测试：无统一 <c>[Route]</c> 前缀，各 action 使用绝对路径。
/// </summary>
[ApiController]
public class RootController(IEmailSender emailSender) : ControllerBase
{
    /// <summary><c>GET /</c>：存活探测，负载均衡健康检查可用。</summary>
    [HttpGet("/")]
    public IActionResult Root() => Ok(new { message = "Hello World" });

    /// <summary><c>GET /hello/{name}</c>：路由模板绑定路径参数示例。</summary>
    [HttpGet("/hello/{name}")]
    public IActionResult Hello(string name) => Ok(new { message = $"Hello {name}" });

    /// <summary><c>GET /mail/test?email=</c>：验证 SMTP 配置（依赖 appsettings 中 Smtp）。</summary>
    [HttpGet("/mail/test")]
    public async Task<IActionResult> MailTest([FromQuery] string email, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(email))
            return BadRequest(new { detail = "email 查询参数必填" });

        try
        {
            await emailSender.SendPlainAsync(email, "hello", $"hello {email}", ct).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }

        return Ok(new { message = "邮件发送成功！" });
    }
}
