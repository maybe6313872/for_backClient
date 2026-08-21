using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>公司 <c>/company/*</c>；删除时会清理关联订单与订单明细。</summary>
[ApiController]
[Route("company")]
public class CompanyController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /company/create</c>；成功时 <c>data</c> 为提示字符串（与旧 API 一致）。</summary>
    [HttpPost("create")]
    public async Task<ActionResult<ArtQueryOutDto>> Create([FromBody] CompanyCreateInDto data, CancellationToken ct)
    {
        try
        {
            db.Companies.Add(new Company { Name = data.Name, Address = data.Address, CreatedTime = DateTime.Now });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ArtQueryOutDto { Data = "created successfully" });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary><c>GET /company/query</c>：无数据时 404，有数据时匿名对象包装。</summary>
    [HttpGet("query")]
    public async Task<IActionResult> Query(CancellationToken ct)
    {
        try
        {
            var list = await db.Companies.AsNoTracking().OrderBy(c => c.Id).ToListAsync(ct).ConfigureAwait(false);
            if (list.Count == 0)
                return NotFound(new { detail = "公司未找到" });
            return Ok(new { code = 200, message = "查询成功", data = list });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary><see cref="ExecuteUpdateAsync"/>：不加载实体，直接生成 UPDATE SQL。</summary>
    [HttpPut("update")]
    public async Task<IActionResult> Update([FromBody] CompanyUpdateInDto data, CancellationToken ct)
    {
        try
        {
            var affected = await db.Companies.Where(c => c.Id == data.Id)
                .ExecuteUpdateAsync(s => s
                    .SetProperty(c => c.Name, data.Name)
                    .SetProperty(c => c.Address, data.Address), ct)
                .ConfigureAwait(false);
            if (affected == 0)
                return StatusCode(500, new { detail = "公司不存在" });
            return Ok(new { code = 200, message = "更新成功", data = 1 });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary>先删订单行、订单头，再删公司，避免外键阻碍。</summary>
    [HttpDelete("delete")]
    public async Task<IActionResult> Delete([FromQuery] int company_id, CancellationToken ct)
    {
        try
        {
            var company = await db.Companies
                .Include(c => c.Orders)
                .FirstOrDefaultAsync(c => c.Id == company_id, ct)
                .ConfigureAwait(false);
            if (company is null)
                return Ok(new { code = 200, message = "删除成功", data = 1 });

            var orderIds = company.Orders.Select(o => o.Id).ToList();
            if (orderIds.Count > 0)
            {
                await db.OrderLines.Where(l => orderIds.Contains(l.OrderId)).ExecuteDeleteAsync(ct).ConfigureAwait(false);
                await db.Orders.Where(o => orderIds.Contains(o.Id)).ExecuteDeleteAsync(ct).ConfigureAwait(false);
            }

            db.Companies.Remove(company);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new { code = 200, message = "删除成功", data = 1 });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }
}
