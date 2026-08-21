// -----------------------------------------------------------------------------
// 用户实体：表名 user；密码列 _password 与 Python SQLAlchemy 一致。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Zhiliao.Ainame.Api.Entities;

/// <summary>
/// 注册用户。
/// <para>本仓库使用 BCrypt 哈希；若数据库来自 Python Argon2 用户，需重置密码后才能用本 API 登录。</para>
/// </summary>
[Table("user")]
public class AppUser
{
    public int Id { get; set; }

    /// <summary>登录账号，唯一索引。</summary>
    [MaxLength(100)]
    public string Email { get; set; } = "";

    [MaxLength(100)]
    public string Username { get; set; } = "";

    /// <summary>与 Python/SQLAlchemy 列名 <c>_password</c> 一致；存 BCrypt 哈希字符串。</summary>
    [Column("_password")]
    [MaxLength(200)]
    public string PasswordHash { get; set; } = "";
}
