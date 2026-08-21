using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 订单 <c>/order/*</c>：先写订单头拿自增 Id，再插多行明细。
/// </summary>
[ApiController]
[Route("order")]
public class OrderController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /order/create</c>：第一次 SaveChanges 得到 <see cref="OrderHeader.Id"/>，再插 <see cref="OrderLine"/>。</summary>
    [HttpPost("create")]
    public async Task<ActionResult<ArtQueryOutDto>> Create([FromBody] OrderInDto data, CancellationToken ct)
    {
        try
        {
            var order = new OrderHeader
            {
                OrderNumber = data.OrderNumber,
                CompanyId = data.CompanyId,
                CreatedTime = DateTime.Now
            };
            db.Orders.Add(order);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);

            foreach (var p in data.ProductList)
            {
                db.OrderLines.Add(new OrderLine
                {
                    OrderId = order.Id,
                    ProductId = p.Id,
                    Number = p.Number,
                    CreatedTime = DateTime.Now
                });
            }

            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ArtQueryOutDto { Data = "created successfully" });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary><c>PUT /order/update</c>：body 须含订单 <c>id</c>；先更新头再删旧明细并重插。</summary>
    [HttpPut("update")]
    public async Task<ActionResult<ArtQueryOutDto>> Update([FromBody] OrderInDto data, CancellationToken ct)
    {
        if (data.Id is null)
            return BadRequest(new { detail = "缺少订单 id" });
        try
        {
            await db.Orders.Where(o => o.Id == data.Id)
                .ExecuteUpdateAsync(s => s
                    .SetProperty(o => o.OrderNumber, data.OrderNumber)
                    .SetProperty(o => o.CompanyId, data.CompanyId), ct)
                .ConfigureAwait(false);

            await db.OrderLines.Where(l => l.OrderId == data.Id).ExecuteDeleteAsync(ct).ConfigureAwait(false);

            foreach (var p in data.ProductList)
            {
                db.OrderLines.Add(new OrderLine
                {
                    OrderId = data.Id.Value,
                    ProductId = p.Id,
                    Number = p.Number,
                    CreatedTime = DateTime.Now
                });
            }

            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ArtQueryOutDto { Data = "updated successfully" });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary>
    /// <c>GET /order/query</c>：逐单加载公司与明细、单价，计算 <c>TotalPrice</c>（教学示例；大数据量应改为单次 SQL 聚合）。
    /// </summary>
    [HttpGet("query")]
    public async Task<ActionResult<OrderQueryApiResponseDto>> Query(CancellationToken ct)
    {
        try
        {
            var orders = await db.Orders.AsNoTracking().OrderBy(o => o.Id).ToListAsync(ct).ConfigureAwait(false);
            var result = new List<OrderQueryRowOutDto>();

            foreach (var o in orders)
            {
                var companyName = await db.Companies.AsNoTracking()
                    .Where(c => c.Id == o.CompanyId)
                    .Select(c => c.Name)
                    .FirstOrDefaultAsync(ct)
                    .ConfigureAwait(false);

                var lines = await db.OrderLines.AsNoTracking().Where(l => l.OrderId == o.Id).ToListAsync(ct).ConfigureAwait(false);
                var plist = new List<OrderProductRowOutDto>();
                float total = 0;
                foreach (var line in lines)
                {
                    var prod = await db.Products.AsNoTracking().FirstOrDefaultAsync(p => p.Id == line.ProductId, ct).ConfigureAwait(false);
                    var price = prod?.Price ?? 0;
                    var num = line.Number ?? 0;
                    total += price * num;
                    plist.Add(new OrderProductRowOutDto
                    {
                        ProductId = line.ProductId,
                        ProductName = prod?.Name,
                        Number = line.Number,
                        Price = price
                    });
                }

                result.Add(new OrderQueryRowOutDto
                {
                    Id = o.Id,
                    OrderNumber = o.OrderNumber,
                    CompanyId = o.CompanyId,
                    CompanyName = companyName,
                    ProductList = plist,
                    TotalPrice = total
                });
            }

            return Ok(new OrderQueryApiResponseDto { Data = result });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }

    /// <summary><c>DELETE /order/delete?id=</c>：先删 <c>order_product</c> 再删 <c>order</c>。</summary>
    [HttpDelete("delete")]
    public async Task<ActionResult<ArtQueryOutDto>> Delete([FromQuery] int id, CancellationToken ct)
    {
        try
        {
            await db.OrderLines.Where(l => l.OrderId == id).ExecuteDeleteAsync(ct).ConfigureAwait(false);
            await db.Orders.Where(o => o.Id == id).ExecuteDeleteAsync(ct).ConfigureAwait(false);
            return Ok(new ArtQueryOutDto { Data = "deleted successfully" });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = ex.Message });
        }
    }
}
