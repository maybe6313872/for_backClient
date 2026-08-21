namespace Zhiliao.Ainame.Api.Options;

/// <summary>
/// SMTP 发信配置，绑定自 appsettings 的 <c>Smtp</c> 节点。
/// </summary>
public class SmtpOptions
{
    public const string SectionName = "Smtp";

    public string Host { get; set; } = "smtp.qq.com";

    public int Port { get; set; } = 587;

    /// <summary>登录 SMTP 的账号，一般为邮箱地址。</summary>
    public string UserName { get; set; } = "";

    /// <summary>授权码（QQ 邮箱在设置里生成），不是网页登录密码。</summary>
    public string Password { get; set; } = "";

    /// <summary>发件人地址；空则回退为 UserName。</summary>
    public string From { get; set; } = "";

    public string FromName { get; set; } = "知了课堂";

    /// <summary>587 端口通常配合 STARTTLS。</summary>
    public bool UseStartTls { get; set; } = true;
}
