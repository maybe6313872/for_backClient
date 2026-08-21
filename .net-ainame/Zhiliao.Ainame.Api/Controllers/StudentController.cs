using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 学生 <c>/student</c>；列表/详情会附带已选课程与成绩（LINQ join 查询）。
/// </summary>
[ApiController]
[Route("student")]
public class StudentController(AppDbContext db) : ControllerBase
{
    /// <summary><c>POST /student</c>：新建学生，须指定已存在的 <c>TeacherId</c>。</summary>
    [HttpPost("")]
    public async Task<ActionResult<ResponseOut>> Create([FromBody] StudentInDto data, CancellationToken ct)
    {
        try
        {
            db.Students.Add(new Student
            {
                Name = data.Name,
                Sex = data.Sex,
                Age = data.Age,
                TeacherId = data.TeacherId,
                CreatedTime = DateTime.Now
            });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"创建学生失败: {ex.Message}" });
        }
    }

    /// <summary>
    /// <c>GET /student</c>：列表；查询参数 <c>teacher_id</c> 可选，用于只看某班学生。
    /// <para>每个学生单独 <see cref="BuildOutAsync"/>，N+1 查询，数据量大时可改为单条 SQL/投影优化。</para>
    /// </summary>
    [HttpGet("")]
    public async Task<ActionResult<StudentListResponseDto>> GetAll([FromQuery] int? teacher_id, CancellationToken ct)
    {
        try
        {
            var q = db.Students.AsNoTracking().AsQueryable();
            if (teacher_id is not null)
                q = q.Where(s => s.TeacherId == teacher_id);
            var students = await q.OrderBy(s => s.Id).ToListAsync(ct).ConfigureAwait(false);
            var data = new List<StudentOutDto>();
            foreach (var s in students)
                data.Add(await BuildOutAsync(s, ct).ConfigureAwait(false));
            return Ok(new StudentListResponseDto { Data = data });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询学生列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /student/{studentId}</c>：详情含 <c>courses</c> 嵌套。</summary>
    [HttpGet("{studentId:int}")]
    public async Task<ActionResult<StudentOutDto>> GetById(int studentId, CancellationToken ct)
    {
        try
        {
            var s = await db.Students.AsNoTracking().FirstOrDefaultAsync(x => x.Id == studentId, ct).ConfigureAwait(false);
            if (s is null)
                return NotFound(new { detail = $"学生ID {studentId} 不存在" });
            return Ok(await BuildOutAsync(s, ct).ConfigureAwait(false));
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询学生失败: {ex.Message}" });
        }
    }

    /// <summary><c>PUT /student/{studentId}</c>：部分更新。</summary>
    [HttpPut("{studentId:int}")]
    public async Task<ActionResult<ResponseOut>> Update(int studentId, [FromBody] StudentUpdateInDto data, CancellationToken ct)
    {
        try
        {
            var s = await db.Students.FirstOrDefaultAsync(x => x.Id == studentId, ct).ConfigureAwait(false);
            if (s is null)
                return NotFound(new { detail = $"学生ID {studentId} 不存在" });
            if (data.Name is not null) s.Name = data.Name;
            if (data.Sex is not null) s.Sex = data.Sex;
            if (data.Age is not null) s.Age = data.Age.Value;
            if (data.TeacherId is not null) s.TeacherId = data.TeacherId.Value;
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"更新学生失败: {ex.Message}" });
        }
    }

    /// <summary>先删选课再删学生，避免外键约束错误。</summary>
    [HttpDelete("{studentId:int}")]
    public async Task<ActionResult<ResponseOut>> Delete(int studentId, CancellationToken ct)
    {
        try
        {
            var s = await db.Students.FirstOrDefaultAsync(x => x.Id == studentId, ct).ConfigureAwait(false);
            if (s is null)
                return NotFound(new { detail = $"学生ID {studentId} 不存在" });
            await db.StudentCourseEnrollments.Where(sc => sc.StudentId == studentId).ExecuteDeleteAsync(ct).ConfigureAwait(false);
            db.Students.Remove(s);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"删除学生失败: {ex.Message}" });
        }
    }

    /// <summary>
    /// 查询语法：from/join/where 会被 EF 翻译成 SQL INNER JOIN。
    /// <see cref="CourseController.MapOut"/> 复用课程 DTO 映射。
    /// </summary>
    private async Task<StudentOutDto> BuildOutAsync(Student s, CancellationToken ct)
    {
        var rows = await (
            from sc in db.StudentCourseEnrollments.AsNoTracking()
            join c in db.Courses.AsNoTracking() on sc.CourseId equals c.Id
            where sc.StudentId == s.Id
            select new { sc.Score, c }
        ).ToListAsync(ct).ConfigureAwait(false);

        var courses = rows.Select(x => new CourseWithScoreDto
        {
            Course = CourseController.MapOut(x.c),
            Score = x.Score
        }).ToList();

        return new StudentOutDto
        {
            Id = s.Id,
            Name = s.Name,
            Sex = s.Sex,
            Age = s.Age,
            TeacherId = s.TeacherId,
            CreatedTime = s.CreatedTime,
            Courses = courses
        };
    }
}
