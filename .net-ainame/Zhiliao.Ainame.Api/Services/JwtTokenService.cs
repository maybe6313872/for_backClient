using System.IdentityModel.Tokens.Jwt;
using System.Text;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using Zhiliao.Ainame.Api.Options;

namespace Zhiliao.Ainame.Api.Services;

/// <summary>
/// JWT 实现：与 Python 版 PyJWT 载荷对齐。
/// <list type="bullet">
/// <item><description><c>iss</c>：用户 id（数值，写入 JWT 后为数字类型）</description></item>
/// <item><description><c>sub</c>：<c>"1"</c> 表示访问令牌，<c>"2"</c> 表示刷新令牌</description></item>
/// <item><description><c>exp</c>：过期时间（Unix 秒）</description></item>
/// </list>
/// <para>登录接口当前只把 <c>AccessToken</c> 返回给客户端；刷新流程可按同样规则扩展。</para>
/// </summary>
public class JwtTokenService(IOptions<JwtOptions> options) : IJwtTokenService
{
    private readonly JwtOptions _opt = options.Value;

    private const string AccessSub = "1";
    private const string RefreshSub = "2";

    public string CreateAccessToken(int userId) => Encode(userId, AccessSub, _opt.AccessTokenDays);

    public string CreateRefreshToken(int userId) => Encode(userId, RefreshSub, _opt.RefreshTokenDays);

    public (string AccessToken, string RefreshToken) CreateLoginTokens(int userId) =>
        (CreateAccessToken(userId), CreateRefreshToken(userId));

    public int GetUserIdFromAccessToken(string token) =>
        Decode(token, AccessSub, "Access Token已过期！", "Access Token不可用！");

    public int GetUserIdFromRefreshToken(string token) =>
        Decode(token, RefreshSub, "Refresh Token已过期！", "Refresh Token不可用！");

    /// <summary>组装 Header+Payload，用 HMAC-SHA256 签名。</summary>
    private string Encode(int userId, string sub, int daysValid)
    {
        var exp = DateTime.UtcNow.AddDays(daysValid);
        var expUnix = new DateTimeOffset(exp).ToUnixTimeSeconds();
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_opt.SecretKey));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        var payload = new JwtPayload
        {
            { "iss", userId },
            { "sub", sub },
            { "exp", expUnix }
        };
        var token = new JwtSecurityToken(new JwtHeader(creds), payload);
        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    /// <summary>
    /// 验签 + 校验过期 + 核对 sub + 从 iss 解析用户 id。
    /// <para>JWT 标准里 iss 通常是字符串，这里与 Python 一致存数字，解析时用 TryParse。</para>
    /// </summary>
    private int Decode(string token, string expectedSub, string expiredMessage, string invalidMessage)
    {
        var handler = new JwtSecurityTokenHandler();
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_opt.SecretKey));
        var parameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = key,
            ValidateIssuer = false,
            ValidateAudience = false,
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromMinutes(1)
        };

        try
        {
            var principal = handler.ValidateToken(token, parameters, out _);
            var sub = principal.FindFirst("sub")?.Value;
            if (sub != expectedSub)
                throw new SecurityTokenException("Token类型错误！");

            // 兼容：有的库会把 iss 映射到 JwtRegisteredClaimNames.Iss
            var iss = principal.FindFirst("iss")?.Value
                ?? principal.FindFirst(JwtRegisteredClaimNames.Iss)?.Value;
            if (iss is null || !int.TryParse(iss, out var userId))
                throw new SecurityTokenException(invalidMessage);

            return userId;
        }
        catch (SecurityTokenExpiredException)
        {
            throw new SecurityTokenException(expiredMessage);
        }
        catch (SecurityTokenException)
        {
            throw;
        }
        catch (Exception ex)
        {
            throw new SecurityTokenException(invalidMessage, ex);
        }
    }
}
