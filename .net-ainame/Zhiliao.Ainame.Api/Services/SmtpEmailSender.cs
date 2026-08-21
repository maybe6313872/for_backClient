using MailKit.Net.Smtp;
using MailKit.Security;
using Microsoft.Extensions.Options;
using MimeKit;
using Zhiliao.Ainame.Api.Options;

namespace Zhiliao.Ainame.Api.Services;

/// <summary>
/// 使用 MailKit 通过 SMTP 发信（QQ 邮箱等需使用「授权码」而非登录密码）。
/// <para>配置来自 <see cref="SmtpOptions"/>（appsettings 的 Smtp 节点）。</para>
/// </summary>
public class SmtpEmailSender(IOptions<SmtpOptions> options) : IEmailSender
{
    private readonly SmtpOptions _smtp = options.Value;

    /// <inheritdoc />
    /// <remarks>
    /// Connect → Authenticate → Send → Disconnect；<c>using</c> 确保连接释放。
    /// <c>UseStartTls</c> 为 true 时常用 587 端口 + STARTTLS。
    /// </remarks>
    public async Task SendPlainAsync(string to, string subject, string body, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(_smtp.UserName) || string.IsNullOrWhiteSpace(_smtp.Password))
            throw new InvalidOperationException("请在配置中设置 Smtp:UserName 与 Smtp:Password。");

        var message = new MimeMessage();
        message.From.Add(new MailboxAddress(_smtp.FromName, string.IsNullOrEmpty(_smtp.From) ? _smtp.UserName : _smtp.From));
        message.To.Add(MailboxAddress.Parse(to));
        message.Subject = subject;
        message.Body = new TextPart("plain") { Text = body };

        using var client = new SmtpClient();
        var secure = _smtp.UseStartTls ? SecureSocketOptions.StartTls : SecureSocketOptions.Auto;
        await client.ConnectAsync(_smtp.Host, _smtp.Port, secure, cancellationToken).ConfigureAwait(false);
        await client.AuthenticateAsync(_smtp.UserName, _smtp.Password, cancellationToken).ConfigureAwait(false);
        await client.SendAsync(message, cancellationToken).ConfigureAwait(false);
        await client.DisconnectAsync(true, cancellationToken).ConfigureAwait(false);
    }
}
