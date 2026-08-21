using Microsoft.EntityFrameworkCore;
using Zhiliao.Ainame.Api.Entities;

namespace Zhiliao.Ainame.Api.Data;

/// <summary>
/// 数据库会话（EF Core 的 DbContext），相当于 SQLAlchemy 的 Session + 所有 Model 的集合。
/// <para>生命周期：每个 HTTP 请求创建一个实例（Scoped），请求结束释放，避免长时间占用连接。</para>
/// <para>表名、列名、外键删除行为在 <see cref="OnModelCreating"/> 里配置，以与 Python/Alembic 已有库结构对齐。</para>
/// <para>不在此处写业务逻辑；仅描述「表如何映射到类」。</para>
/// </summary>
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    // 每个 DbSet<T> 暴露一张表的 LINQ 入口；SaveChanges 时把跟踪到的变更生成 INSERT/UPDATE/DELETE

    /// <summary>注册用户表 <c>user</c>。</summary>
    public DbSet<AppUser> Users => Set<AppUser>();

    /// <summary>邮箱验证码表 <c>email_code</c>。</summary>
    public DbSet<EmailCode> EmailCodes => Set<EmailCode>();

    /// <summary>文章表 <c>art</c>。</summary>
    public DbSet<Art> Arts => Set<Art>();

    /// <summary>学校表 <c>school</c>。</summary>
    public DbSet<School> Schools => Set<School>();

    /// <summary>教师表 <c>teacher</c>。</summary>
    public DbSet<Teacher> Teachers => Set<Teacher>();

    /// <summary>学生表 <c>student</c>。</summary>
    public DbSet<Student> Students => Set<Student>();
    /// <summary>课程表 <c>course</c>。</summary>
    public DbSet<CourseEntity> Courses => Set<CourseEntity>();

    /// <summary>选课中间表 <c>student_course</c>。</summary>
    public DbSet<StudentCourseEnrollment> StudentCourseEnrollments => Set<StudentCourseEnrollment>();

    /// <summary>公司表 <c>company</c>。</summary>
    public DbSet<Company> Companies => Set<Company>();

    /// <summary>产品表 <c>product</c>。</summary>
    public DbSet<ProductItem> Products => Set<ProductItem>();

    /// <summary>订单头表 <c>order</c>。</summary>
    public DbSet<OrderHeader> Orders => Set<OrderHeader>();

    /// <summary>订单明细表 <c>order_product</c>。</summary>
    public DbSet<OrderLine> OrderLines => Set<OrderLine>();

    /// <summary>
    ///  Fluent API 配置：优先级高于实体类上的 DataAnnotations（二者可混用）。
    /// </summary>
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // ----- 用户与验证码 -----
        modelBuilder.Entity<AppUser>(e =>
        {
            e.ToTable("user"); // 物理表名与 Python 一致（user 在 SQL 中常为保留字，故显式指定）
            e.HasIndex(x => x.Email).IsUnique(); // 与业务「邮箱唯一」一致
            e.Property(x => x.PasswordHash).HasColumnName("_password"); // C# 属性名不能与列名一致时用 HasColumnName
        });

        modelBuilder.Entity<EmailCode>(e => { e.ToTable("email_code"); });

        // ----- 文章：缩略图二进制 -----
        modelBuilder.Entity<Art>(e =>
        {
            e.ToTable("art");
            e.Property(x => x.Thumbnail).HasColumnType("longblob"); // MySQL 大二进制
        });

        // ----- 校园：删除学校 → 级联删教师 → 级联删学生；选课表由控制器先删 -----
        modelBuilder.Entity<School>(e =>
        {
            e.ToTable("school");
            e.HasMany(x => x.Teachers)
                .WithOne(x => x.School!)
                .HasForeignKey(x => x.SchoolId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Teacher>(e =>
        {
            e.ToTable("teacher");
            e.HasMany(x => x.Students)
                .WithOne(x => x.Teacher!)
                .HasForeignKey(x => x.TeacherId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        modelBuilder.Entity<Student>(e => { e.ToTable("student"); });

        modelBuilder.Entity<CourseEntity>(e => { e.ToTable("course"); });

        // 选课：复合唯一 (StudentId, CourseId)；删学生或删课程时级联删选课行
        modelBuilder.Entity<StudentCourseEnrollment>(e =>
        {
            e.ToTable("student_course");
            e.HasIndex(x => new { x.StudentId, x.CourseId }).IsUnique();
            e.HasOne(x => x.Student).WithMany().HasForeignKey(x => x.StudentId).OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.Course).WithMany().HasForeignKey(x => x.CourseId).OnDelete(DeleteBehavior.Cascade);
        });

        // ----- 订单域 -----
        // 删公司时若不允许级联删订单，用 Restrict，由控制器手动删订单再删公司
        modelBuilder.Entity<Company>(e =>
        {
            e.ToTable("company");
            e.HasMany(x => x.Orders)
                .WithOne(x => x.Company!)
                .HasForeignKey(x => x.CompanyId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        modelBuilder.Entity<ProductItem>(e => { e.ToTable("product"); });

        modelBuilder.Entity<OrderHeader>(e =>
        {
            e.ToTable("order");
            e.HasMany(x => x.OrderLines)
                .WithOne(x => x.Order!)
                .HasForeignKey(x => x.OrderId)
                .OnDelete(DeleteBehavior.Cascade); // 删订单头时明细一并删
        });

        // 订单明细：同一订单同一商品唯一一行；删产品时 Restrict 防止误删仍被订单引用的商品
        modelBuilder.Entity<OrderLine>(e =>
        {
            e.ToTable("order_product");
            e.HasIndex(x => new { x.OrderId, x.ProductId }).IsUnique();
            e.HasOne(x => x.Product).WithMany(x => x.OrderLines).HasForeignKey(x => x.ProductId).OnDelete(DeleteBehavior.Restrict);
        });
    }
}
