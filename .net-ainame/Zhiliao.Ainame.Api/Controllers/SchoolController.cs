using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>学校 REST：<c>/school</c>；删除学校时会先删关联学生的选课再级联删师生（见实现）。</summary>
[ApiController]
[Route("school")]
public class SchoolController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /school</c>：创建一条学校记录。</summary>
    [HttpPost("")]
    public async Task<ActionResult<ResponseOut>> Create([FromBody] SchoolInDto data, CancellationToken ct)
    {
        try
        {
            db.Schools.Add(new School { Name = data.Name, Address = data.Address, CreatedTime = DateTime.Now });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"创建学校失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /school</c>：全部学校，按 Id 升序。</summary>
    [HttpGet("")]
    public async Task<ActionResult<SchoolListResponseDto>> GetAll(CancellationToken ct)
    {
        try
        {
            var schools = await db.Schools.AsNoTracking().OrderBy(x => x.Id).ToListAsync(ct).ConfigureAwait(false);
            var data = schools.Select(s => new SchoolOutDto
            {
                Id = s.Id,
                Name = s.Name,
                Address = s.Address,
                CreatedTime = s.CreatedTime
            }).ToList();
            return Ok(new SchoolListResponseDto { Data = data });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询学校列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /school/{schoolId}</c>：按主键查询。</summary>
    [HttpGet("{schoolId:int}")]
    public async Task<ActionResult<SchoolOutDto>> GetById(int schoolId, CancellationToken ct)
    {
        try
        {
            var s = await db.Schools.AsNoTracking().FirstOrDefaultAsync(x => x.Id == schoolId, ct).ConfigureAwait(false);
            if (s is null)
                return NotFound(new { detail = $"学校ID {schoolId} 不存在" });
            return Ok(new SchoolOutDto { Id = s.Id, Name = s.Name, Address = s.Address, CreatedTime = s.CreatedTime });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询学校失败: {ex.Message}" });
        }
    }

    /// <summary><c>PUT /school/{schoolId}</c>：部分更新，仅提交的非 null 字段生效。</summary>
    [HttpPut("{schoolId:int}")]
    public async Task<ActionResult<ResponseOut>> Update(int schoolId, [FromBody] SchoolUpdateInDto data, CancellationToken ct)
    {
        try
        {
            var s = await db.Schools.FirstOrDefaultAsync(x => x.Id == schoolId, ct).ConfigureAwait(false);
            if (s is null)
                return NotFound(new { detail = $"学校ID {schoolId} 不存在" });
            if (data.Name is not null) s.Name = data.Name;
            if (data.Address is not null) s.Address = data.Address;
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"更新学校失败: {ex.Message}" });
        }
    }

    /// <summary>
    /// 删除学校：Include 加载所有班主任与学生，先删这些学生的选课记录，再 Remove 学校（触发级联删师生）。
    /// <para>若不加这一步，<c>student_course</c> 可能残留外键指向已删学生。</para>
    /// </summary>
    [HttpDelete("{schoolId:int}")]
    public async Task<ActionResult<ResponseOut>> Delete(int schoolId, CancellationToken ct)
    {
        try
        {
            var school = await db.Schools
                .Include(x => x.Teachers)
                .ThenInclude(t => t.Students)
                .FirstOrDefaultAsync(x => x.Id == schoolId, ct)
                .ConfigureAwait(false);
            if (school is null)
                return NotFound(new { detail = $"学校ID {schoolId} 不存在" });

            var studentIds = school.Teachers.SelectMany(t => t.Students).Select(s => s.Id).ToList();
            if (studentIds.Count > 0)
                await db.StudentCourseEnrollments.Where(sc => studentIds.Contains(sc.StudentId)).ExecuteDeleteAsync(ct).ConfigureAwait(false);

            db.Schools.Remove(school);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"删除学校失败: {ex.Message}" });
        }
    }
}
