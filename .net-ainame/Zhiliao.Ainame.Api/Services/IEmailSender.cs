namespace Zhiliao.Ainame.Api.Services;

/// <summary>
/// 邮件发送抽象：注册页验证码、/mail/test 等都通过它发信，具体实现为 <see cref="SmtpEmailSender"/>。
/// </summary>
public interface IEmailSender
{
    /// <summary>发送纯文本邮件。</summary>
    Task SendPlainAsync(string to, string subject, string body, CancellationToken cancellationToken = default);
}
