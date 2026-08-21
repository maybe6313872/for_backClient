using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>课程 <c>/course</c>。</summary>
[ApiController]
[Route("course")]
public class CourseController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /course</c>：新建课程。</summary>
    [HttpPost("")]
    public async Task<ActionResult<ResponseOut>> Create([FromBody] CourseInDto data, CancellationToken ct)
    {
        try
        {
            db.Courses.Add(new CourseEntity { Name = data.Name, Credit = data.Credit, CreatedTime = DateTime.Now });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"创建课程失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /course</c>：全部课程。</summary>
    [HttpGet("")]
    public async Task<ActionResult<CourseListResponseDto>> GetAll(CancellationToken ct)
    {
        try
        {
            var list = await db.Courses.AsNoTracking().OrderBy(c => c.Id).ToListAsync(ct).ConfigureAwait(false);
            var data = list.Select(MapOut).ToList();
            return Ok(new CourseListResponseDto { Data = data });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询课程列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /course/{courseId}</c>。</summary>
    [HttpGet("{courseId:int}")]
    public async Task<ActionResult<CourseOutDto>> GetById(int courseId, CancellationToken ct)
    {
        try
        {
            var c = await db.Courses.AsNoTracking().FirstOrDefaultAsync(x => x.Id == courseId, ct).ConfigureAwait(false);
            if (c is null)
                return NotFound(new { detail = $"课程ID {courseId} 不存在" });
            return Ok(MapOut(c));
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询课程失败: {ex.Message}" });
        }
    }

    /// <summary><c>PUT /course/{courseId}</c>：部分更新名称或学分。</summary>
    [HttpPut("{courseId:int}")]
    public async Task<ActionResult<ResponseOut>> Update(int courseId, [FromBody] CourseUpdateInDto data, CancellationToken ct)
    {
        try
        {
            var c = await db.Courses.FirstOrDefaultAsync(x => x.Id == courseId, ct).ConfigureAwait(false);
            if (c is null)
                return NotFound(new { detail = $"课程ID {courseId} 不存在" });
            if (data.Name is not null) c.Name = data.Name;
            if (data.Credit is not null) c.Credit = data.Credit.Value;
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"更新课程失败: {ex.Message}" });
        }
    }

    /// <summary>删课前先删 <c>student_course</c> 中引用该课的记录。</summary>
    [HttpDelete("{courseId:int}")]
    public async Task<ActionResult<ResponseOut>> Delete(int courseId, CancellationToken ct)
    {
        try
        {
            var c = await db.Courses.FirstOrDefaultAsync(x => x.Id == courseId, ct).ConfigureAwait(false);
            if (c is null)
                return NotFound(new { detail = $"课程ID {courseId} 不存在" });
            await db.StudentCourseEnrollments.Where(sc => sc.CourseId == courseId).ExecuteDeleteAsync(ct).ConfigureAwait(false);
            db.Courses.Remove(c);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"删除课程失败: {ex.Message}" });
        }
    }

    /// <summary><c>internal</c>：供同程序集 <see cref="StudentController"/> 复用，避免重复映射代码。</summary>
    internal static CourseOutDto MapOut(CourseEntity c) => new()
    {
        Id = c.Id,
        Name = c.Name,
        Credit = c.Credit,
        CreatedTime = c.CreatedTime
    };
}
