// -----------------------------------------------------------------------------
// 从 FastAPI 迁移来的各模块请求/响应 DTO（文章、校园、订单、省市区等）。
//
// 阅读提示：
//   • [Required]、[Range] 等与 FastAPI Body 的校验规则对应；失败时 ASP.NET Core 自动 400。
//   • 属性名默认序列化为 snake_case（见 Program.cs），与 Python 侧 pydantic 别名一致；
//     少数字段用 [JsonPropertyName] 固定 JSON 名（如订单里的 id/number、msg）。
//   • 「列表包装」类（如 SchoolListResponseDto）含 code/message/data，兼容旧前端。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace Zhiliao.Ainame.Api.Contracts;

#region 文章后台 Art / Admin

/// <summary>批量删除文章：请求体中的 id 列表。</summary>
public class ArtDeleteIn
{
    /// <summary>要删除的文章主键集合；不可为空列表。</summary>
    [Required, MinLength(1)]
    public List<int> IdArr { get; set; } = [];
}

/// <summary>修改文章（当前仅支持改性别字段，与 Python 接口一致）。</summary>
public class ArtChangeIn
{
    /// <summary>文章主键。</summary>
    [Required]
    public int Id { get; set; }

    /// <summary>新性别值。</summary>
    [Required, MaxLength(10)]
    public string Sex { get; set; } = "";
}

/// <summary>文章分页查询条件（按性别过滤）。</summary>
public class ArtQueryIn
{
    /// <summary>页码，从 1 开始。</summary>
    [Range(1, int.MaxValue)]
    public int Page { get; set; } = 1;

    /// <summary>每页条数，最大 100。</summary>
    [Range(1, 100)]
    public int Size { get; set; } = 10;

    /// <summary>筛选性别。</summary>
    [Required, MaxLength(10)]
    public string Sex { get; set; } = "";
}

/// <summary>单条文章列表项（不含缩略图二进制，减轻响应体积）。</summary>
public class ArtOutDto
{
    public int Id { get; set; }
    public string Username { get; set; } = "";
    public string Sex { get; set; } = "";
    /// <summary>正文内容。</summary>
    public string Artcontent { get; set; } = "";
}

/// <summary>带包装层的查询结果（code/message/data）。</summary>
public class ArtQueryOutDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    /// <summary>可能是列表、数字或字符串，视接口而定（与 Python 灵活返回对齐）。</summary>
    public object? Data { get; set; }
}

#endregion

#region 学校 School

/// <summary>创建学校。</summary>
public class SchoolInDto
{
    [Required, MaxLength(100)]
    public string Name { get; set; } = "";

    [Required, MaxLength(200)]
    public string Address { get; set; } = "";
}

/// <summary>学校详情输出。</summary>
public class SchoolOutDto
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Address { get; set; } = "";
    public DateTime CreatedTime { get; set; }
}

/// <summary>部分更新：仅非 null 字段覆盖。</summary>
public class SchoolUpdateInDto
{
    [MaxLength(100)]
    public string? Name { get; set; }

    [MaxLength(200)]
    public string? Address { get; set; }
}

/// <summary>学校列表 API 包装响应。</summary>
public class SchoolListResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<SchoolOutDto> Data { get; set; } = [];
}

#endregion

#region 班主任 Teacher

/// <summary>创建班主任；必须属于已存在的 <c>SchoolId</c>。</summary>
public class TeacherInDto
{
    [Required, MaxLength(50)]
    public string Name { get; set; } = "";

    [Required, MaxLength(10)]
    public string Sex { get; set; } = "";

    [Range(0, 150)]
    public int Age { get; set; }

    [Required]
    public int SchoolId { get; set; }
}

/// <summary>班主任 API 输出。</summary>
public class TeacherOutDto
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Sex { get; set; } = "";
    public int Age { get; set; }
    public int SchoolId { get; set; }
    public DateTime CreatedTime { get; set; }
}

/// <summary>部分更新班主任信息。</summary>
public class TeacherUpdateInDto
{
    [MaxLength(50)]
    public string? Name { get; set; }

    [MaxLength(10)]
    public string? Sex { get; set; }

    [Range(0, 150)]
    public int? Age { get; set; }

    public int? SchoolId { get; set; }
}

/// <summary>班主任列表包装。</summary>
public class TeacherListResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<TeacherOutDto> Data { get; set; } = [];
}

#endregion

#region 课程 Course

/// <summary>创建课程请求体。</summary>
public class CourseInDto
{
    [Required, MaxLength(100)]
    public string Name { get; set; } = "";

    /// <summary>学分。</summary>
    [Required]
    public float Credit { get; set; }
}

/// <summary>课程输出 DTO。</summary>
public class CourseOutDto
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public float Credit { get; set; }
    public DateTime CreatedTime { get; set; }
}

/// <summary>部分更新课程。</summary>
public class CourseUpdateInDto
{
    [MaxLength(100)]
    public string? Name { get; set; }
    public float? Credit { get; set; }
}

/// <summary>课程列表包装。</summary>
public class CourseListResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<CourseOutDto> Data { get; set; } = [];
}

#endregion

#region 学生 Student

/// <summary>学生详情里嵌套的一门课 + 该生该课成绩。</summary>
public class CourseWithScoreDto
{
    public CourseOutDto Course { get; set; } = null!;
    public float? Score { get; set; }
}

/// <summary>创建学生；须指定已存在的 <c>TeacherId</c>。</summary>
public class StudentInDto
{
    [Required, MaxLength(50)]
    public string Name { get; set; } = "";

    [Required, MaxLength(10)]
    public string Sex { get; set; } = "";

    [Range(0, 150)]
    public int Age { get; set; }

    [Required]
    public int TeacherId { get; set; }
}

/// <summary>学生输出：含已选课程列表（由控制器 join 查询组装）。</summary>
public class StudentOutDto
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Sex { get; set; } = "";
    public int Age { get; set; }
    public int TeacherId { get; set; }
    public DateTime CreatedTime { get; set; }
    public List<CourseWithScoreDto> Courses { get; set; } = [];
}

/// <summary>部分更新学生字段。</summary>
public class StudentUpdateInDto
{
    [MaxLength(50)]
    public string? Name { get; set; }

    [MaxLength(10)]
    public string? Sex { get; set; }

    [Range(0, 150)]
    public int? Age { get; set; }

    public int? TeacherId { get; set; }
}

/// <summary>学生列表 API 包装。</summary>
public class StudentListResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<StudentOutDto> Data { get; set; } = [];
}

#endregion

#region 选课 Student-course

/// <summary>单条选课记录创建。</summary>
public class StudentCourseInDto
{
    [Required]
    public int StudentId { get; set; }

    [Required]
    public int CourseId { get; set; }

    /// <summary>可选成绩，0～100。</summary>
    [Range(0, 100)]
    public float? Score { get; set; }
}

/// <summary>单条选课记录输出。</summary>
public class StudentCourseOutDto
{
    public int Id { get; set; }
    public int StudentId { get; set; }
    public int CourseId { get; set; }
    public float? Score { get; set; }
    public DateTime CreatedTime { get; set; }
}

/// <summary>更新选课成绩。</summary>
public class StudentCourseUpdateInDto
{
    [Range(0, 100)]
    public float? Score { get; set; }
}

/// <summary>
/// 批量替换某学生的全部选课：服务端会先删该学生所有选课再插入。
/// <para><see cref="Scores"/> 与 <see cref="CourseIds"/> 按下标一一对应；若省略 Scores 则无成绩。</para>
/// </summary>
public class StudentCourseBatchInDto
{
    [Required]
    public int StudentId { get; set; }

    [Required, MinLength(1)]
    public List<int> CourseIds { get; set; } = [];

    public List<float>? Scores { get; set; }
}

/// <summary>按课程查询时的学生行（扁平结构，方便表格展示）。</summary>
public class StudentWithScoreDto
{
    public int StudentId { get; set; }
    public string StudentName { get; set; } = "";
    public string StudentSex { get; set; } = "";
    public int StudentAge { get; set; }
    public int TeacherId { get; set; }
    public float? Score { get; set; }
}

/// <summary>选课列表包装。</summary>
public class StudentCourseListResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<StudentCourseOutDto> Data { get; set; } = [];
}

/// <summary>按课程查学生列表的包装。</summary>
public class StudentsByCourseResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<StudentWithScoreDto> Data { get; set; } = [];
}

#endregion

#region 订单域 Company / Product / Order

/// <summary>新建公司请求体。</summary>
public class CompanyCreateInDto
{
    [Required, MaxLength(100)]
    public string Name { get; set; } = "";

    [Required, MaxLength(200)]
    public string Address { get; set; } = "";
}

/// <summary>按主键全量更新公司名称与地址。</summary>
public class CompanyUpdateInDto
{
    [Required]
    public int Id { get; set; }

    [Required, MaxLength(100)]
    public string Name { get; set; } = "";

    [Required, MaxLength(200)]
    public string Address { get; set; } = "";
}

/// <summary>
/// 产品创建或更新共用形状；<see cref="Id"/> 为空表示创建，有值表示更新（由具体接口使用）。
/// </summary>
public class ProductInDto
{
    public int? Id { get; set; }

    [Required, MaxLength(100)]
    public string Name { get; set; } = "";

    [Required]
    public float Price { get; set; }

    /// <summary>库存数量（字段名与历史库列 storenum 一致）。</summary>
    [Required]
    public int Storenum { get; set; }

    [Required, MaxLength(200)]
    public string Description { get; set; } = "";

    [Required, MaxLength(200)]
    public string Productno { get; set; } = "";
}

/// <summary>订单里的一行商品：JSON 属性名为小写 id、number（与旧客户端约定）。</summary>
public class OrderLineItemDto
{
    [JsonPropertyName("id")]
    public int Id { get; set; }

    /// <summary>购买数量。</summary>
    [JsonPropertyName("number")]
    public float Number { get; set; }
}

/// <summary>
/// 创建或更新订单：头信息 + 明细列表。
/// <para>更新时 <see cref="Id"/> 为订单主键；创建时为空。</para>
/// </summary>
public class OrderInDto
{
    public int? Id { get; set; }

    [Required, MaxLength(100)]
    public string OrderNumber { get; set; } = "";

    [Required]
    public int CompanyId { get; set; }

    [Required]
    public List<OrderLineItemDto> ProductList { get; set; } = [];
}

/// <summary>订单查询结果中的单行商品（含单价，用于算总价）。</summary>
public class OrderProductRowOutDto
{
    public int ProductId { get; set; }
    public string? ProductName { get; set; }
    public float? Number { get; set; }
    public float Price { get; set; }
}

/// <summary>单笔订单的聚合展示（含明细与总价）。</summary>
public class OrderQueryRowOutDto
{
    public int Id { get; set; }
    public string OrderNumber { get; set; } = "";
    public int CompanyId { get; set; }
    public string? CompanyName { get; set; }
    public List<OrderProductRowOutDto> ProductList { get; set; } = [];
    public float TotalPrice { get; set; }
}

/// <summary>订单列表接口外层；<c>msg</c> 为 JSON 字段名（非 message）。</summary>
public class OrderQueryApiResponseDto
{
    public int Code { get; set; } = 200;
    public List<OrderQueryRowOutDto> Data { get; set; } = [];

    [JsonPropertyName("msg")]
    public string Msg { get; set; } = "success";
}

#endregion

#region 省市区 Region（HTTP 响应包装）

/// <summary>省市区列表的统一包装（code/message/data）。</summary>
public class RegionListResponseDto
{
    public int Code { get; set; } = 200;
    public string Message { get; set; } = "查询成功";
    public List<RegionItemDto> Data { get; set; } = [];
}

/// <summary>省/市/区一项：行政区划代码 + 名称。</summary>
public class RegionItemDto
{
    public string Code { get; set; } = "";
    public string Name { get; set; } = "";
}

#endregion
