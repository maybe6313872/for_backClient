using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>产品 <c>/product/*</c>。</summary>
[ApiController]
[Route("product")]
public class ProductController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /product/create</c>；创建时无需 body 里的 Id。</summary>
    [HttpPost("create")]
    public async Task<ActionResult<ArtQueryOutDto>> Create([FromBody] ProductInDto data, CancellationToken ct)
    {
        try
        {
            db.Products.Add(new ProductItem
            {
                Name = data.Name,
                Price = data.Price,
                Storenum = data.Storenum,
                Description = data.Description,
                Productno = data.Productno,
                CreatedTime = DateTime.Now
            });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ArtQueryOutDto { Data = "created successfully" });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary><c>GET /product/query</c>：全部产品列表。</summary>
    [HttpGet("query")]
    public async Task<IActionResult> Query(CancellationToken ct)
    {
        try
        {
            var list = await db.Products.AsNoTracking().OrderBy(p => p.Id).ToListAsync(ct).ConfigureAwait(false);
            return Ok(new { code = 200, message = "查询成功", data = list });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary><c>PUT /product/update</c>：body 必须带 <c>id</c>（产品主键）。</summary>
    [HttpPut("update")]
    public async Task<IActionResult> Update([FromBody] ProductInDto data, CancellationToken ct)
    {
        if (data.Id is null)
            return BadRequest(new { detail = "缺少产品 id" });
        try
        {
            var affected = await db.Products.Where(p => p.Id == data.Id)
                .ExecuteUpdateAsync(s => s
                    .SetProperty(p => p.Name, data.Name)
                    .SetProperty(p => p.Price, data.Price)
                    .SetProperty(p => p.Storenum, data.Storenum)
                    .SetProperty(p => p.Description, data.Description)
                    .SetProperty(p => p.Productno, data.Productno), ct)
                .ConfigureAwait(false);
            if (affected == 0)
                return StatusCode(500, new { detail = "产品不存在" });
            return Ok(new { code = 200, message = "更新成功", data = 1 });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary>
    /// 删除产品：查询参数名故意与 Python 拼写一致 <c>prduct_id</c>（历史兼容）。
    /// <para>若产品出现在订单明细中，会先删掉相关订单的全部明细（与迁移策略一致，学习时请对照业务是否接受）。</para>
    /// </summary>
    [HttpDelete("delete")]
    public async Task<IActionResult> Delete([FromQuery(Name = "prduct_id")] int prduct_id, CancellationToken ct)
    {
        try
        {
            var product = await db.Products
                .Include(p => p.OrderLines)
                .FirstOrDefaultAsync(p => p.Id == prduct_id, ct)
                .ConfigureAwait(false);
            if (product is null)
                return Ok(new { code = 200, message = "删除成功", data = 1 });

            var orderIds = product.OrderLines.Select(l => l.OrderId).Distinct().ToList();
            if (orderIds.Count > 0)
                await db.OrderLines.Where(l => orderIds.Contains(l.OrderId)).ExecuteDeleteAsync(ct).ConfigureAwait(false);

            db.Products.Remove(product);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new { code = 200, message = "删除成功", data = 1 });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }
}
