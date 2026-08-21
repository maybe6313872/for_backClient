// -----------------------------------------------------------------------------
// 邮箱验证码记录：注册时校验最近一条是否在有效时间窗口内。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Zhiliao.Ainame.Api.Entities;

/// <summary>
/// 对应表 <c>email_code</c>。
/// <para>AuthController 取同一邮箱最新一条记录，与请求中 code 比对，且创建时间在 10 分钟内。</para>
/// </summary>
[Table("email_code")]
public class EmailCode
{
    public int Id { get; set; }

    [MaxLength(100)]
    public string Email { get; set; } = "";

    /// <summary>通常为 4 位数字字符串。</summary>
    [MaxLength(10)]
    public string Code { get; set; } = "";

    /// <summary>服务端生成验证码的时间。</summary>
    public DateTime CreatedTime { get; set; }

    /// <summary>业务类型占位，如 test。</summary>
    [MaxLength(10)]
    public string Type { get; set; } = "test";
}
