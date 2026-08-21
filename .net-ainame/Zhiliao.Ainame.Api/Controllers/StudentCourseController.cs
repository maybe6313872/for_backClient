using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Contracts;
using Zhiliao.Ainame.Api.Data;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Controllers;

/// <summary>
/// 学生选课中间表 <c>/student-course</c>。
/// <para>批量提交会先清空该学生原选课再插入新行，保证与 Python「整表替换」语义一致。</para>
/// </summary>
[ApiController]
[Route("student-course")]
public class StudentCourseController(AppDbContext db) : ControllerBase
{
    /// <summary>
    /// 批量选课：显式事务 + 先 <c>ExecuteDeleteAsync</c> 再循环 <c>Add</c>。
    /// <para>若 <c>Scores</c> 非空，长度必须与 <c>CourseIds</c> 一致（按索引对应成绩）。</para>
    /// </summary>
    [HttpPost("")]
    public async Task<ActionResult<ResponseOut>> BatchReplace([FromBody] StudentCourseBatchInDto data, CancellationToken ct)
    {
        try
        {
            if (data.Scores is not null && data.Scores.Count != data.CourseIds.Count)
                return BadRequest(new { detail = "分数数组长度必须与课程ID数组长度一致" });

            await using var tx = await db.Database.BeginTransactionAsync(ct).ConfigureAwait(false);
            await db.StudentCourseEnrollments.Where(sc => sc.StudentId == data.StudentId).ExecuteDeleteAsync(ct).ConfigureAwait(false);

            for (var i = 0; i < data.CourseIds.Count; i++)
            {
                float? score = data.Scores is not null ? data.Scores[i] : null;
                db.StudentCourseEnrollments.Add(new StudentCourseEnrollment
                {
                    StudentId = data.StudentId,
                    CourseId = data.CourseIds[i],
                    Score = score,
                    CreatedTime = DateTime.Now
                });
            }

            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            await tx.CommitAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"批量创建学生课程关联失败: {ex.Message}" });
        }
    }

    /// <summary>单条插入选课；数据库唯一索引防止同一学生同一课重复。</summary>
    [HttpPost("single")]
    public async Task<ActionResult<ResponseOut>> CreateSingle([FromBody] StudentCourseInDto data, CancellationToken ct)
    {
        try
        {
            var exists = await db.StudentCourseEnrollments.AnyAsync(
                sc => sc.StudentId == data.StudentId && sc.CourseId == data.CourseId,
                ct).ConfigureAwait(false);
            if (exists)
                return BadRequest(new { detail = "该学生已选修此课程" });

            db.StudentCourseEnrollments.Add(new StudentCourseEnrollment
            {
                StudentId = data.StudentId,
                CourseId = data.CourseId,
                Score = data.Score,
                CreatedTime = DateTime.Now
            });
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"创建学生课程关联失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /student-course/course/{courseId}/students</c>：某课下学生及成绩。</summary>
    [HttpGet("course/{courseId:int}/students")]
    public async Task<ActionResult<StudentsByCourseResponseDto>> GetStudentsByCourse(int courseId, CancellationToken ct)
    {
        try
        {
            var rows = await (
                from sc in db.StudentCourseEnrollments.AsNoTracking()
                join st in db.Students.AsNoTracking() on sc.StudentId equals st.Id
                where sc.CourseId == courseId
                orderby st.Id
                select new StudentWithScoreDto
                {
                    StudentId = st.Id,
                    StudentName = st.Name,
                    StudentSex = st.Sex,
                    StudentAge = st.Age,
                    TeacherId = st.TeacherId,
                    Score = sc.Score
                }
            ).ToListAsync(ct).ConfigureAwait(false);

            return Ok(new StudentsByCourseResponseDto { Data = rows });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询课程学生列表失败: {ex.Message}" });
        }
    }

    /// <summary>
    /// <c>GET /student-course</c>：查询参数 <c>student_id</c> 与 <c>course_id</c> 二选一（与 Python 一致）；
    /// 若都不传则返回全部关联（数据量大时注意性能）。
    /// </summary>
    [HttpGet("")]
    public async Task<ActionResult<StudentCourseListResponseDto>> GetAll(
        [FromQuery] int? student_id,
        [FromQuery] int? course_id,
        CancellationToken ct)
    {
        try
        {
            var q = db.StudentCourseEnrollments.AsNoTracking().AsQueryable();
            if (student_id is not null)
                q = q.Where(sc => sc.StudentId == student_id);
            else if (course_id is not null)
                q = q.Where(sc => sc.CourseId == course_id);

            var list = await q.OrderBy(sc => sc.Id).ToListAsync(ct).ConfigureAwait(false);
            var data = list.Select(sc => new StudentCourseOutDto
            {
                Id = sc.Id,
                StudentId = sc.StudentId,
                CourseId = sc.CourseId,
                Score = sc.Score,
                CreatedTime = sc.CreatedTime
            }).ToList();
            return Ok(new StudentCourseListResponseDto { Data = data });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询学生课程关联列表失败: {ex.Message}" });
        }
    }

    /// <summary><c>GET /student-course/{id}</c>：选课中间表主键。</summary>
    [HttpGet("{id:int}")]
    public async Task<ActionResult<StudentCourseOutDto>> GetById(int id, CancellationToken ct)
    {
        try
        {
            var sc = await db.StudentCourseEnrollments.AsNoTracking().FirstOrDefaultAsync(x => x.Id == id, ct).ConfigureAwait(false);
            if (sc is null)
                return NotFound(new { detail = $"关联记录ID {id} 不存在" });
            return Ok(new StudentCourseOutDto
            {
                Id = sc.Id,
                StudentId = sc.StudentId,
                CourseId = sc.CourseId,
                Score = sc.Score,
                CreatedTime = sc.CreatedTime
            });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"查询学生课程关联失败: {ex.Message}" });
        }
    }

    /// <summary><c>PUT /student-course/{id}</c>：通常用于改成绩。</summary>
    [HttpPut("{id:int}")]
    public async Task<ActionResult<ResponseOut>> Update(int id, [FromBody] StudentCourseUpdateInDto data, CancellationToken ct)
    {
        try
        {
            var sc = await db.StudentCourseEnrollments.FirstOrDefaultAsync(x => x.Id == id, ct).ConfigureAwait(false);
            if (sc is null)
                return NotFound(new { detail = $"关联记录ID {id} 不存在" });
            if (data.Score is not null)
                sc.Score = data.Score;
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"更新学生课程关联失败: {ex.Message}" });
        }
    }

    /// <summary><c>DELETE /student-course/{id}</c>：退选一条记录。</summary>
    [HttpDelete("{id:int}")]
    public async Task<ActionResult<ResponseOut>> Delete(int id, CancellationToken ct)
    {
        try
        {
            var sc = await db.StudentCourseEnrollments.FirstOrDefaultAsync(x => x.Id == id, ct).ConfigureAwait(false);
            if (sc is null)
                return NotFound(new { detail = $"关联记录ID {id} 不存在" });
            db.StudentCourseEnrollments.Remove(sc);
            await db.SaveChangesAsync(ct).ConfigureAwait(false);
            return Ok(new ResponseOut());
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { detail = $"删除学生课程关联失败: {ex.Message}" });
        }
    }
}
