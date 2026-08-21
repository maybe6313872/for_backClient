// -----------------------------------------------------------------------------
// 认证、起名等 API 的请求/响应 DTO。
//
// • [ApiController] 会自动对带有校验特性的模型进行验证，失败返回 400 + ProblemDetails，
//   概念上接近 FastAPI 依赖 Body 里的 Pydantic 模型。
// • 实现 IValidatableObject 可在跨字段规则（如两次密码一致）里返回自定义错误。
// • JSON 序列化为 snake_case（Program.cs），故前端收到 user_name 等形式（按属性名转换规则）。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;

namespace Zhiliao.Ainame.Api.Contracts;

/// <summary>通用成功占位（如注册成功只返回 result: success）。</summary>
public class ResponseOut
{
    /// <summary>固定或业务约定的结果标识。</summary>
    public string Result { get; set; } = "success";
}

/// <summary>注册：邮箱 + 用户名 + 密码确认 + 邮箱验证码。</summary>
public class RegisterRequest : IValidatableObject
{
    /// <summary>将作为登录账号，唯一。</summary>
    [Required, EmailAddress]
    public string Email { get; set; } = "";

    [Required, MinLength(3), MaxLength(20)]
    public string Username { get; set; } = "";

    /// <summary>明文密码；服务端仅存 BCrypt 哈希。</summary>
    [Required, MinLength(6), MaxLength(20)]
    public string Password { get; set; } = "";

    /// <summary>必须与 <see cref="Password"/> 一致，由 <see cref="Validate"/> 校验。</summary>
    [Required, MinLength(6), MaxLength(20)]
    public string ConfirmPassword { get; set; } = "";

    /// <summary>4 位数字验证码，与 /auth/code 下发的一致。</summary>
    [Required, MinLength(4), MaxLength(4)]
    public string Code { get; set; } = "";

    /// <inheritdoc />
    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (Password != ConfirmPassword)
            yield return new ValidationResult("两个密码不一致！", [nameof(ConfirmPassword)]);
    }
}

/// <summary>登录：邮箱 + 密码。</summary>
public class LoginRequest
{
    [Required, EmailAddress]
    public string Email { get; set; } = "";

    [Required, MinLength(6), MaxLength(20)]
    public string Password { get; set; } = "";
}

/// <summary>返回给前端的用户信息（绝不返回密码或哈希）。</summary>
public class UserDto
{
    public int Id { get; set; }
    public string Email { get; set; } = "";
    public string Username { get; set; } = "";
}

/// <summary>登录成功：用户信息 + JWT 访问令牌（放入 Authorization: Bearer）。</summary>
public class LoginResponse
{
    public UserDto User { get; set; } = null!;

    /// <summary>访问令牌（非刷新令牌）；过期时间由 Jwt:AccessTokenDays 配置。</summary>
    public string Token { get; set; } = "";
}

/// <summary>起名接口入参（当前控制器为 mock，字段预留给真实算法）。</summary>
public class NameRequest
{
    /// <summary>姓氏。</summary>
    [Required]
    public string Surname { get; set; } = "";

    /// <summary>期望性别：不限 / 男 / 女。</summary>
    [Required]
    [RegularExpression("^(不限|男|女)$")]
    public string Gender { get; set; } = "不限";

    /// <summary>名字字数：不限 / 单字 / 两字。</summary>
    [Required]
    [RegularExpression("^(不限|单字|两字)$")]
    public string Length { get; set; } = "不限";

    /// <summary>其它偏好说明，可选。</summary>
    public string? Other { get; set; }

    /// <summary>排除用字列表。</summary>
    public List<string> Exclude { get; set; } = [];
}

/// <summary>单个推荐名及出处、寓意说明。</summary>
public class NameItemDto
{
    public string Name { get; set; } = "";
    public string Reference { get; set; } = "";
    public string Moral { get; set; } = "";
}

/// <summary>起名接口返回的列表。</summary>
public class NameResponse
{
    public List<NameItemDto> Names { get; set; } = [];
}
