using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>班主任 <c>/teacher</c>；可选查询参数 <c>school_id</c> 过滤。</summary>
[ApiController]
[Route("teacher")]
public class TeacherController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /teacher</c>：新建班主任，须指定已存在的 <c>SchoolId</c>。</summary>
    [HttpPost("")]
    public async Task<ActionResult<ResponseOut>> Create([FromBody] TeacherInDto data, CancellationToken ct)
    {
        try
        {
            db.Teachers.Add(new Teacher
            {
                Name = data.Name,
                Sex = data.Sex,
                Age = data.Age,
                SchoolId = data.SchoolId,
                CreatedTime = DateTime.Now
            });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"创建班主任失败: {ex.Message}" });
        }
    }

    /// <summary>列表；<c>school_id</c> 有值时只返回该校老师。</summary>
    [HttpGet("")]
    public async Task<ActionResult<TeacherListResponseDto>> GetAll([FromQuery] int? school_id, CancellationToken ct)
    {
        try
        {
            var q = db.Teachers.AsNoTracking().AsQueryable();
            if (school_id is not null)
                q = q.Where(t => t.SchoolId == school_id);
            var list = await q.OrderBy(t => t.Id).ToListAsync(ct).ConfigureAwait(false);
            var data = list.Select(MapOut).ToList();
            return Ok(new TeacherListResponseDto { Data = data });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询班主任列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /teacher/{teacherId}</c>：单条查询。</summary>
    [HttpGet("{teacherId:int}")]
    public async Task<ActionResult<TeacherOutDto>> GetById(int teacherId, CancellationToken ct)
    {
        try
        {
            var t = await db.Teachers.AsNoTracking().FirstOrDefaultAsync(x => x.Id == teacherId, ct).ConfigureAwait(false);
            if (t is null)
                return NotFound(new { detail = $"班主任ID {teacherId} 不存在" });
            return Ok(MapOut(t));
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询班主任失败: {ex.Message}" });
        }
    }

    /// <summary><c>PUT /teacher/{teacherId}</c>：部分更新。</summary>
    [HttpPut("{teacherId:int}")]
    public async Task<ActionResult<ResponseOut>> Update(int teacherId, [FromBody] TeacherUpdateInDto data, CancellationToken ct)
    {
        try
        {
            var t = await db.Teachers.FirstOrDefaultAsync(x => x.Id == teacherId, ct).ConfigureAwait(false);
            if (t is null)
                return NotFound(new { detail = $"班主任ID {teacherId} 不存在" });
            if (data.Name is not null) t.Name = data.Name;
            if (data.Sex is not null) t.Sex = data.Sex;
            if (data.Age is not null) t.Age = data.Age.Value;
            if (data.SchoolId is not null) t.SchoolId = data.SchoolId.Value;
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"更新班主任失败: {ex.Message}" });
        }
    }

    /// <summary>删除班主任前先删掉其所有学生的选课行，再级联删学生。</summary>
    [HttpDelete("{teacherId:int}")]
    public async Task<ActionResult<ResponseOut>> Delete(int teacherId, CancellationToken ct)
    {
        try
        {
            var teacher = await db.Teachers.Include(t => t.Students).FirstOrDefaultAsync(t => t.Id == teacherId, ct).ConfigureAwait(false);
            if (teacher is null)
                return NotFound(new { detail = $"班主任ID {teacherId} 不存在" });

            var studentIds = teacher.Students.Select(s => s.Id).ToList();
            if (studentIds.Count > 0)
                await db.StudentCourseEnrollments.Where(sc => studentIds.Contains(sc.StudentId)).ExecuteDeleteAsync(ct).ConfigureAwait(false);

            db.Teachers.Remove(teacher);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"删除班主任失败: {ex.Message}" });
        }
    }

    /// <summary>实体 → 输出 DTO，无导航属性展开。</summary>
    private static TeacherOutDto MapOut(Teacher t) => new()
    {
        Id = t.Id,
        Name = t.Name,
        Sex = t.Sex,
        Age = t.Age,
        SchoolId = t.SchoolId,
        CreatedTime = t.CreatedTime
    };
}
