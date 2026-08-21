// -----------------------------------------------------------------------------
// 文章实体：对应表 art；缩略图以 byte[] 映射 MySQL LONGBLOB。
// -----------------------------------------------------------------------------

using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Zhiliao.Ainame.Api.Entities;

/// <summary>
/// 后台文章/作品。
/// <para>与 AdminArtController  multipart 上传、Excel 导入共用此表结构。</para>
/// </summary>
[Table("art")]
public class Art
{
    public int Id { get; set; }

    [MaxLength(100)]
    public string Username { get; set; } = "";

    [MaxLength(10)]
    public string Sex { get; set; } = "";

    /// <summary>正文，最长 5000 字符（与校验一致）。</summary>
    [MaxLength(5000)]
    public string Artcontent { get; set; } = "";

    /// <summary>缩略图二进制；列表接口通常不返回以减小流量。</summary>
    public byte[] Thumbnail { get; set; } = [];

    public DateTime CreatedTime { get; set; }
}
