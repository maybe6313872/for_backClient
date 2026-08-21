namespace Zhiliao.Ainame.Api.Services;

/// <summary>
/// JWT 签发与解析抽象，便于单元测试时替换为假实现。
/// <para>与 Python 版约定一致：<c>iss</c> 存用户 id，<c>sub</c> 区分访问令牌/刷新令牌。</para>
/// </summary>
public interface IJwtTokenService
{
    /// <summary>签发短期访问令牌（sub="1"）。</summary>
    /// <param name="userId">写入 JWT 的 <c>iss</c> 声明。</param>
    string CreateAccessToken(int userId);

    /// <summary>签发长期刷新令牌（sub="2"）；当前登录接口只返回访问令牌。</summary>
    /// <param name="userId">用户主键。</param>
    string CreateRefreshToken(int userId);

    /// <param name="userId">用户主键。</param>
    (string AccessToken, string RefreshToken) CreateLoginTokens(int userId);

    /// <summary>校验访问令牌并解析出用户 id；失败抛 SecurityTokenException。</summary>
    /// <param name="token">不含 Bearer 前缀的裸 JWT 字符串。</param>
    int GetUserIdFromAccessToken(string token);

    /// <param name="token">刷新令牌字符串。</param>
    int GetUserIdFromRefreshToken(string token);
}
