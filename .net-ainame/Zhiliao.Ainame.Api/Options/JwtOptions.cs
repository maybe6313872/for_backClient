namespace Zhiliao.Ainame.Api.Options;

/// <summary>
/// JWT 相关配置，绑定自 appsettings 的 <c>Jwt</c> 节点。
/// <para><c>SecretKey</c> 必须足够长且保密；开发可用 User Secrets，生产用环境变量或密钥保管库。</para>
/// </summary>
public class JwtOptions
{
    public const string SectionName = "Jwt";

    /// <summary>对称签名密钥（与 Program.cs 里 TokenValidationParameters 使用同一把）。</summary>
    public string SecretKey { get; set; } = "";

    /// <summary>访问令牌有效天数。</summary>
    public int AccessTokenDays { get; set; } = 15;

    /// <summary>刷新令牌有效天数。</summary>
    public int RefreshTokenDays { get; set; } = 30;
}
