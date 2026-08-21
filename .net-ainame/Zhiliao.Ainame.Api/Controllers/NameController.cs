using Microsoft.AspNetCore.Mvc;
using Zhiliao.Ainame.Api.Contracts;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>起名接口：<c>POST /name</c>；当前返回固定示例，与 Python 侧 mock 一致。</summary>
[ApiController]
[Route("name")]
public class NameController : ControllerBase
{
    /// <summary>
    /// <c>POST /name</c>：占位实现；可在此接入大模型或业务规则引擎。
    /// <para><paramref name="_"/> 仅占位避免未使用警告；实现时可改用姓氏、性别等字段。</para>
    /// </summary>
    [HttpPost]
    [ProducesResponseType(typeof(NameResponse), StatusCodes.Status200OK)]
    public ActionResult<NameResponse> Generate([FromBody] NameRequest _)
    {
        return Ok(new NameResponse
        {
            Names =
            [
                new NameItemDto
                {
                    Name = "张子涵",
                    Reference = "《诗经·小雅》",
                    Moral = "子：有学问、有德行的人；涵：包容、涵养"
                }
            ]
        });
    }
}
