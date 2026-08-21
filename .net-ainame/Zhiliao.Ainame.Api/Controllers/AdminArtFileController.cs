using System.Globalization;
using System.Net;
using ClosedXML.Excel;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 文章与 Excel：<c>queryArtExcel</c> 导出 xlsx，<c>insertArtByExcel</c> 批量导入。
/// <para>ClosedXML 主要面向 <c>.xlsx</c>；扩展名允许 <c>.xls</c> 时若格式过旧可能解析失败。</para>
/// </summary>
[ApiController]
[Route("admin")]
public class AdminArtFileController(AppDbContext db) : ControllerBase
{
    /// <summary>
    /// <c>POST /admin/queryArtExcel</c>：按条件查文章并返回 xlsx 附件。
    /// <para><c>Content-Disposition</c> 含 ASCII 文件名与 RFC 5987 <c>filename*</c>，减少中文名乱码。</para>
    /// </summary>
    [HttpPost("queryArtExcel")]
    public async Task<IActionResult> QueryArtExcel([FromBody] ArtQueryIn data, CancellationToken ct)
    {
        var arts = await db.Arts.AsNoTracking()
            .Where(a => a.Sex == data.Sex)
            .OrderByDescending(a => a.CreatedTime)
            .Skip((data.Page - 1) * data.Size)
            .Take(data.Size)
            .ToListAsync(ct)
            .ConfigureAwait(false);

        using var wb = new XLWorkbook();
        var ws = wb.Worksheets.Add("文章列表");
        ws.Cell(1, 1).Value = "ID";
        ws.Cell(1, 2).Value = "用户名";
        ws.Cell(1, 3).Value = "性别";
        ws.Cell(1, 4).Value = "文章内容";
        var header = ws.Range(1, 1, 1, 4);
        header.Style.Font.Bold = true;
        header.Style.Font.FontColor = XLColor.White;
        header.Style.Fill.BackgroundColor = XLColor.FromHtml("#366092");
        header.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;

        var row = 2;
        foreach (var a in arts)
        {
            ws.Cell(row, 1).Value = a.Id;
            ws.Cell(row, 2).Value = a.Username;
            ws.Cell(row, 3).Value = a.Sex;
            ws.Cell(row, 4).Value = a.Artcontent;
            row++;
        }

        ws.Column(1).Width = 10;
        ws.Column(2).Width = 20;
        ws.Column(3).Width = 10;
        ws.Column(4).Width = 50;

        await using var stream = new MemoryStream();
        wb.SaveAs(stream);
        var bytes = stream.ToArray();
        var ts = DateTime.Now.ToString("yyyyMMdd_HHmmss", CultureInfo.InvariantCulture);
        var filename = $"文章列表_{ts}.xlsx";
        var ascii = $"article_list_{ts}.xlsx";
        var encoded = WebUtility.UrlEncode(filename).Replace("+", "%20", StringComparison.Ordinal);
        Response.Headers.ContentDisposition = $"attachment; filename=\"{ascii}\"; filename*=UTF-8''{encoded}";
        return File(bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    }

    /// <summary>
    /// <c>POST /admin/insertArtByExcel</c>：按表头别名匹配列，缩略图列可为 Base64。
    /// <para>先累积内存再统一 <see cref="DbContext.SaveChangesAsync"/>；部分行失败时见返回 <c>detail</c>。</para>
    /// </summary>
    [HttpPost("insertArtByExcel")]
    [Consumes("multipart/form-data")]
    public async Task<ActionResult<ResponseOut>> InsertArtByExcel(IFormFile file, CancellationToken ct, [FromForm] string? username = null)
    {
        _ = username;
        var fn = file.FileName ?? "";
        if (!fn.EndsWith(".xlsx", StringComparison.OrdinalIgnoreCase) && !fn.EndsWith(".xls", StringComparison.OrdinalIgnoreCase))
            return BadRequest(new { detail = "文件格式错误，仅支持 .xlsx 或 .xls 格式" });

        await using var upload = new MemoryStream();
        await file.CopyToAsync(upload, ct).ConfigureAwait(false);

        List<string> headers;
        List<Dictionary<int, string?>> rows;
        try
        {
            (headers, rows) = ParseExcel(upload.ToArray());
        }
        catch (Exception ex)
        {
            return BadRequest(new { detail = ex.Message });
        }

        if (rows.Count == 0)
            return BadRequest(new { detail = "Excel文件为空或没有数据行" });

        var colUser = FindColumn(headers, "用户名", "username", "用户");
        var colSex = FindColumn(headers, "性别", "sex");
        var colContent = FindColumn(headers, "文章内容", "artcontent", "内容", "content");
        var colThumb = FindColumn(headers, "缩略图", "thumbnail", "图片", "image");

        if (colUser < 0)
            return BadRequest(new { detail = "Excel文件中缺少'用户名'列" });
        if (colSex < 0)
            return BadRequest(new { detail = "Excel文件中缺少'性别'列" });
        if (colContent < 0)
            return BadRequest(new { detail = "Excel文件中缺少'文章内容'列" });

        var errors = new List<string>();
        var success = 0;

        var rowNum = 2;
        foreach (var cells in rows)
        {
            try
            {
                var u = GetCell(cells, colUser);
                var s = GetCell(cells, colSex);
                var c = GetCell(cells, colContent);
                var th = colThumb >= 0 ? GetCell(cells, colThumb) : null;

                if (string.IsNullOrWhiteSpace(u) || string.IsNullOrWhiteSpace(s) || string.IsNullOrWhiteSpace(c))
                {
                    errors.Add($"第{rowNum}行：缺少必需字段（用户名、性别、文章内容）");
                    rowNum++;
                    continue;
                }

                u = u.Trim();
                s = s.Trim();
                c = c.Trim();
                if (u.Length > 100) { errors.Add($"第{rowNum}行：用户名长度超过100字符"); rowNum++; continue; }
                if (s.Length > 10) { errors.Add($"第{rowNum}行：性别长度超过10字符"); rowNum++; continue; }
                if (c.Length > 5000) { errors.Add($"第{rowNum}行：文章内容长度超过5000字符"); rowNum++; continue; }

                byte[] thumbBytes = [];
                if (!string.IsNullOrWhiteSpace(th))
                {
                    try
                    {
                        thumbBytes = Convert.FromBase64String(th.Trim());
                    }
                    catch
                    {
                        errors.Add($"第{rowNum}行：缩略图base64解码失败，将使用空缩略图");
                    }
                }

                db.Arts.Add(new Art
                {
                    Username = u,
                    Sex = s,
                    Artcontent = c,
                    Thumbnail = thumbBytes,
                    CreatedTime = DateTime.Now
                });
                success++;
            }
            catch (Exception ex)
            {
                errors.Add($"第{rowNum}行处理失败: {ex.Message}");
            }

            rowNum++;
        }

        if (success > 0)
            await db.SaveChangesAsync(ct).ConfigureAwait(false);

        if (success == 0)
        {
            var msg = $"批量导入失败，共{errors.Count}条错误。";
            if (errors.Count > 0)
                msg += " 前5条错误：" + string.Join("; ", errors.Take(5));
            return BadRequest(new { detail = msg });
        }

        return Ok(new ResponseOut());
    }

    /// <summary>读第一张工作表：第一行为表头，从第二行起为数据；全空行跳过。</summary>
    private static (List<string> Headers, List<Dictionary<int, string?>> Rows) ParseExcel(byte[] content)
    {
        using var stream = new MemoryStream(content);
        using var wb = new XLWorkbook(stream);
        var ws = wb.Worksheets.FirstOrDefault() ?? throw new InvalidOperationException("工作簿为空");
        var range = ws.RangeUsed() ?? throw new InvalidOperationException("工作表为空");

        var headers = new List<string>();
        foreach (var cell in range.Row(1).CellsUsed())
            headers.Add(cell.GetString().Trim());

        var rows = new List<Dictionary<int, string?>>();
        for (var r = 2; r <= range.RowCount(); r++)
        {
            var dict = new Dictionary<int, string?>();
            for (var c = 1; c <= range.ColumnCount(); c++)
            {
                var v = ws.Cell(r, c).GetFormattedString();
                dict[c] = string.IsNullOrWhiteSpace(v) ? null : v;
            }
            if (dict.Values.All(string.IsNullOrWhiteSpace))
                continue;
            rows.Add(dict);
        }

        return (headers, rows);
    }

    /// <summary>表头列索引从 1 开始，与 ClosedXML 单元格列号一致。</summary>
    private static int FindColumn(IReadOnlyList<string> headers, params string[] aliases)
    {
        for (var i = 0; i < headers.Count; i++)
        {
            var h = headers[i].Trim();
            if (aliases.Any(a => string.Equals(h, a, StringComparison.OrdinalIgnoreCase)))
                return i + 1;
        }
        return -1;
    }

    private static string? GetCell(Dictionary<int, string?> cells, int col1Based) =>
        cells.TryGetValue(col1Based, out var v) ? v : null;
}
