using Microsoft.AspNetCore.Mvc;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Services;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 省市区三级联动，数据来自 Redis（<see cref="RegionDataService"/>）。
/// <para>查询参数名 <c>province_code</c> / <c>city_code</c> 与 Python 查询字符串一致。</para>
/// </summary>
[ApiController]
[Route("region")]
public class RegionController(RegionDataService region) : ControllerBase
{
    /// <summary><c>GET /region/provinces</c>：依赖 Redis；首次访问会写入示例数据。</summary>
    [HttpGet("provinces")]
    public async Task<ActionResult<RegionListResponseDto>> GetProvinces(CancellationToken ct)
    {
        try
        {
            var list = await region.GetProvincesAsync(ct).ConfigureAwait(false);
            var data = list.Select(x => new RegionItemDto { Code = x.Code, Name = x.Name }).ToList();
            var msg = data.Count == 0 ? "暂无数据" : "查询成功";
            return Ok(new RegionListResponseDto { Code = 200, Message = msg, Data = data });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"获取省份列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /region/cities?province_code=</c>：非法省份返回 404。</summary>
    [HttpGet("cities")]
    public async Task<ActionResult<RegionListResponseDto>> GetCities([FromQuery] string province_code, CancellationToken ct)
    {
        try
        {
            var list = await region.GetCitiesAsync(province_code, ct).ConfigureAwait(false);
            var data = list.Select(x => new RegionItemDto { Code = x.Code, Name = x.Name }).ToList();
            var msg = data.Count == 0 ? "该省份暂无城市数据" : "查询成功";
            return Ok(new RegionListResponseDto { Code = 200, Message = msg, Data = data });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { detail = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"获取城市列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /region/districts?city_code=</c>。</summary>
    [HttpGet("districts")]
    public async Task<ActionResult<RegionListResponseDto>> GetDistricts([FromQuery] string city_code, CancellationToken ct)
    {
        try
        {
            var list = await region.GetDistrictsAsync(city_code, ct).ConfigureAwait(false);
            var data = list.Select(x => new RegionItemDto { Code = x.Code, Name = x.Name }).ToList();
            var msg = data.Count == 0 ? "该城市暂无区县数据" : "查询成功";
            return Ok(new RegionListResponseDto { Code = 200, Message = msg, Data = data });
        }
        catch (KeyNotFoundException ex)
        {
            return NotFound(new { detail = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"获取区县列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>POST /region/init</c>：若 Redis 中尚无省份集合则写入示例省市区。</summary>
    [HttpPost("init")]
    public async Task<IActionResult> Init(CancellationToken ct)
    {
        try
        {
            await region.EnsureInitializedAsync(ct).ConfigureAwait(false);
            return Ok(new { code = 200, message = "省市区数据初始化成功" });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"初始化数据失败: {ex.Message}" });
        }
    }
}
