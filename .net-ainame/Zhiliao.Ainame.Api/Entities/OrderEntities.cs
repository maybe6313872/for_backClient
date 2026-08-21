// -----------------------------------------------------------------------------
// 订单域实体：公司、产品、订单头、订单明细。
// 表名与 Python/SQLAlchemy 一致；注意 order、product 等为常见保留词，依赖 [Table] 显式映射。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Zhiliao.Ainame.Api.Entities;

/// <summary>客户公司，对应表 <c>company</c>；一对多订单 <see cref="OrderHeader"/>。</summary>
[Table("company")]
public class Company
{
    /// <summary>主键，自增。</summary>
    public int Id { get; set; }

    [MaxLength(100)]
    public string Name { get; set; } = "";

    [MaxLength(200)]
    public string Address { get; set; } = "";

    public DateTime CreatedTime { get; set; }

    /// <summary>导航：删除公司前控制器会处理下属订单。</summary>
    public ICollection<OrderHeader> Orders { get; set; } = new List<OrderHeader>();
}

/// <summary>产品 SKU，对应表 <c>product</c>。</summary>
[Table("product")]
public class ProductItem
{
    public int Id { get; set; }

    [MaxLength(100)]
    public string Name { get; set; } = "";

    /// <summary>单价。</summary>
    public float Price { get; set; }

    /// <summary>库存数量（列名 storenum 历史拼写）。</summary>
    public int Storenum { get; set; }

    [MaxLength(200)]
    public string Description { get; set; } = "";

    [MaxLength(200)]
    public string Productno { get; set; } = "";

    public DateTime CreatedTime { get; set; }

    /// <summary>导航：出现在哪些订单明细中。</summary>
    public ICollection<OrderLine> OrderLines { get; set; } = new List<OrderLine>();
}

/// <summary>订单头，对应表 <c>order</c>（MySQL 中表名可能需反引号）。</summary>
[Table("order")]
public class OrderHeader
{
    public int Id { get; set; }

    [MaxLength(100)]
    public string OrderNumber { get; set; } = "";

    /// <summary>外键：所属公司。</summary>
    public int CompanyId { get; set; }

    public Company? Company { get; set; }

    public DateTime CreatedTime { get; set; }

    public ICollection<OrderLine> OrderLines { get; set; } = new List<OrderLine>();
}

/// <summary>
/// 订单明细，对应表 <c>order_product</c>。
/// <para>一行表示「某订单购买了某商品多少件」；同一订单下同一商品唯一索引。</para>
/// </summary>
[Table("order_product")]
public class OrderLine
{
    public int Id { get; set; }

    public int OrderId { get; set; }

    public OrderHeader? Order { get; set; }

    public int ProductId { get; set; }

    public ProductItem? Product { get; set; }

    /// <summary>购买数量。</summary>
    public float? Number { get; set; }

    public DateTime CreatedTime { get; set; }
}
