using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 文章后台 CRUD，路由前缀 <c>/admin</c>；与 Python  multipart / JSON 接口对齐。
/// <para><c>queryArt</c> 需 JWT（<see cref="AuthorizeAttribute"/>），其它端点与迁移前 Python 行为一致（若 Python 未加鉴权则此处可对照调整）。</para>
/// </summary>
[ApiController]
[Route("admin")]
public class AdminArtController(AppDbContext db) : ControllerBase
{
    private const long MaxThumbnailBytes = 100L * 1024 * 1024;

    /// <summary>
    /// <c>POST /admin/insertArt</c>（<c>multipart/form-data</c>）：用户名、性别、正文 + 缩略图文件，二进制写入 <see cref="Art.Thumbnail"/>。
    /// </summary>
    [HttpPost("insertArt")]
    [Consumes("multipart/form-data")]
    [ProducesResponseType(typeof(ResponseOut), StatusCodes.Status200OK)]
    public async Task<ActionResult<ResponseOut>> InsertArt(
        [FromForm] string username,
        [FromForm] string sex,
        [FromForm] string artcontent,
        IFormFile file,
        CancellationToken ct)
    {
        await using var ms = new MemoryStream();
        await file.CopyToAsync(ms, ct).ConfigureAwait(false);
        var thumbnailBytes = ms.ToArray();
        if (thumbnailBytes.Length > MaxThumbnailBytes)
            return StatusCode(413, new { detail = $"文件大小超过限制，最大允许 {MaxThumbnailBytes / 1024 / 1024}MB" });

        try
        {
            db.Arts.Add(new Art
            {
                Username = username,
                Sex = sex,
                Artcontent = artcontent,
                Thumbnail = thumbnailBytes,
                CreatedTime = DateTime.Now
            });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }

        return Ok(new ResponseOut());
    }

    /// <summary><c>POST /admin/delArt</c>：body 传 id 数组；<see cref="ExecuteDeleteAsync"/> 直接生成 DELETE SQL。</summary>
    [HttpPost("delArt")]
    public async Task<ActionResult<int>> DelArt([FromBody] ArtDeleteIn data, CancellationToken ct)
    {
        if (data.IdArr.Count == 0)
            return BadRequest(new { detail = "ID数组不能为空" });

        try
        {
            var affected = await db.Arts.Where(a => data.IdArr.Contains(a.Id)).ExecuteDeleteAsync(ct).ConfigureAwait(false);
            if (affected == 0)
                return BadRequest(new { detail = "未找到要删除的文章记录" });
            return Ok(affected);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"删除失败：{ex.Message}" });
        }
    }

    /// <summary><c>POST /admin/changeArt</c>：只更新性别字段（与 Python 一致）。</summary>
    [HttpPost("changeArt")]
    public async Task<ActionResult<ArtQueryOutDto>> ChangeArt([FromBody] ArtChangeIn data, CancellationToken ct)
    {
        var art = await db.Arts.FirstOrDefaultAsync(a => a.Id == data.Id, ct).ConfigureAwait(false);
        if (art is null)
            return NotFound(new { detail = "文章不存在" });
        art.Sex = data.Sex;
        await db.SaveChangesAsync(ct).ConfigureAwait(false);
        return Ok(new ArtQueryOutDto { Code = 200, Message = "修改成功", Data = art.Id });
    }

    /// <summary><c>POST /admin/queryArt</c>：需 Bearer Token；不返回缩略图二进制。</summary>
    [Authorize]
    [HttpPost("queryArt")]
    public async Task<ActionResult<List<ArtOutDto>>> QueryArt([FromBody] ArtQueryIn data, CancellationToken ct)
    {
        var list = await QueryArtsAsync(data).ConfigureAwait(false);
        return Ok(list);
    }

    /// <summary><c>POST /admin/queryArtOut</c>：与 queryArt 数据相同，多一层 code/message（无 JWT 要求）。</summary>
    [HttpPost("queryArtOut")]
    public async Task<ActionResult<ArtQueryOutDto>> QueryArtOut([FromBody] ArtQueryIn data, CancellationToken ct)
    {
        var list = await QueryArtsAsync(data).ConfigureAwait(false);
        return Ok(new ArtQueryOutDto { Code = 200, Message = "查询成功", Data = list });
    }

    /// <summary><see cref="AsNoTracking"/>：只读查询，EF 不跟踪变更，略省内存。</summary>
    private async Task<List<ArtOutDto>> QueryArtsAsync(ArtQueryIn data)
    {
        var q = db.Arts.AsNoTracking().Where(a => a.Sex == data.Sex).OrderByDescending(a => a.CreatedTime);
        var items = await q.Skip((data.Page - 1) * data.Size).Take(data.Size).ToListAsync().ConfigureAwait(false);
        return items.Select(a => new ArtOutDto
        {
            Id = a.Id,
            Username = a.Username,
            Sex = a.Sex,
            Artcontent = a.Artcontent
        }).ToList();
    }
}
