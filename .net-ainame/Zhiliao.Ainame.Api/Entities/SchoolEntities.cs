// -----------------------------------------------------------------------------
// 校园域实体：学校 → 班主任（教师）→ 学生；课程与多对多中间表 student_course。
// 级联删除在 AppDbContext 中配置；删除学校/教师时控制器会额外清理选课，避免孤儿行。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Zhiliao.Ainame.Api.Entities;

/// <summary>学校；一对多 <see cref="Teacher"/>。</summary>
[Table("school")]
public class School
{
    public int Id { get; set; }

    [MaxLength(100)]
    public string Name { get; set; } = "";

    [MaxLength(200)]
    public string Address { get; set; } = "";

    public DateTime CreatedTime { get; set; }

    /// <summary>导航属性：EF Include/ThenInclude 加载；删学校时遍历学生以清选课。</summary>
    public ICollection<Teacher> Teachers { get; set; } = new List<Teacher>();
}

/// <summary>班主任（教师），归属一所 <see cref="School"/>，带多名 <see cref="Student"/>。</summary>
[Table("teacher")]
public class Teacher
{
    public int Id { get; set; }

    [MaxLength(50)]
    public string Name { get; set; } = "";

    [MaxLength(10)]
    public string Sex { get; set; } = "";

    public int Age { get; set; }

    /// <summary>外键：所属学校。</summary>
    public int SchoolId { get; set; }

    public School? School { get; set; }

    public DateTime CreatedTime { get; set; }

    public ICollection<Student> Students { get; set; } = new List<Student>();
}

/// <summary>学生，归属一名 <see cref="Teacher"/>（班级维度）。</summary>
[Table("student")]
public class Student
{
    public int Id { get; set; }

    [MaxLength(50)]
    public string Name { get; set; } = "";

    [MaxLength(10)]
    public string Sex { get; set; } = "";

    public int Age { get; set; }

    public int TeacherId { get; set; }

    public Teacher? Teacher { get; set; }

    public DateTime CreatedTime { get; set; }
}

/// <summary>课程；与学生的多对多由 <see cref="StudentCourseEnrollment"/> 连接。</summary>
[Table("course")]
public class CourseEntity
{
    public int Id { get; set; }

    [MaxLength(100)]
    public string Name { get; set; } = "";

    public float Credit { get; set; }

    public DateTime CreatedTime { get; set; }
}

/// <summary>
/// 选课/成绩中间表 <c>student_course</c>。
/// <para>数据库唯一索引 (StudentId, CourseId) 防止重复选课。</para>
/// </summary>
[Table("student_course")]
public class StudentCourseEnrollment
{
    public int Id { get; set; }

    public int StudentId { get; set; }

    public Student? Student { get; set; }

    public int CourseId { get; set; }

    public CourseEntity? Course { get; set; }

    public float? Score { get; set; }

    public DateTime CreatedTime { get; set; }
}
