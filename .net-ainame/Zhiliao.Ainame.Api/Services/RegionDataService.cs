using StackExchange.Redis;

namespace Zhiliao.Ainame.Api.Services;

/// <summary>
/// 省市区数据：存于 Redis，结构与 Python <c>routers/redisTest.py</c> 中示例一致。
/// <para>首次访问时若 Key 不存在，会把内存里的 <see cref="SampleData"/> 写入 Redis（演示用，非生产全量行政区划）。</para>
/// </summary>
public class RegionDataService
{
    private readonly IConnectionMultiplexer? _mux;

    public RegionDataService(IConnectionMultiplexer? mux) => _mux = mux;

    // Redis Key 命名：集合存 code 列表，Hash 存 code/name 详情
    private const string ProvincesSetKey = "region:provinces:set";
    private const string ProvinceInfoKeyTpl = "region:province:{0}:info";
    private const string ProvinceCitiesKeyTpl = "region:province:{0}:cities:set";
    private const string CityInfoKeyTpl = "region:city:{0}:info";
    private const string CityDistrictsKeyTpl = "region:city:{0}:districts:set";
    private const string DistrictInfoKeyTpl = "region:district:{0}:info";

    /// <summary>懒连接：只有真正访问 Redis 时才要求连接串已配置。</summary>
    private IDatabase Db =>
        _mux?.GetDatabase() ?? throw new InvalidOperationException("未配置 Redis:ConnectionString，省市区接口不可用。");

    /// <summary>若省份集合不存在，则批量写入示例省/市/区数据。</summary>
    public async Task EnsureInitializedAsync(CancellationToken ct = default)
    {
        if (await Db.KeyExistsAsync(ProvincesSetKey).ConfigureAwait(false))
            return;

        var (provinces, cities, districts) = SampleData();

        foreach (var (code, name) in provinces)
        {
            await Db.SetAddAsync(ProvincesSetKey, code).ConfigureAwait(false);
            await Db.HashSetAsync(string.Format(ProvinceInfoKeyTpl, code), new[]
            {
                new HashEntry("code", code),
                new HashEntry("name", name)
            }).ConfigureAwait(false);
        }

        foreach (var (provinceCode, cityList) in cities)
        {
            foreach (var (cCode, cName) in cityList)
            {
                await Db.HashSetAsync(string.Format(CityInfoKeyTpl, cCode), new[]
                {
                    new HashEntry("code", cCode),
                    new HashEntry("name", cName)
                }).ConfigureAwait(false);
                await Db.SetAddAsync(string.Format(ProvinceCitiesKeyTpl, provinceCode), cCode).ConfigureAwait(false);
            }
        }

        foreach (var (cityCode, distList) in districts)
        {
            foreach (var (dCode, dName) in distList)
            {
                await Db.HashSetAsync(string.Format(DistrictInfoKeyTpl, dCode), new[]
                {
                    new HashEntry("code", dCode),
                    new HashEntry("name", dName)
                }).ConfigureAwait(false);
                await Db.SetAddAsync(string.Format(CityDistrictsKeyTpl, cityCode), dCode).ConfigureAwait(false);
            }
        }
    }

    public async Task<IReadOnlyList<RegionInfoDto>> GetProvincesAsync(CancellationToken ct = default)
    {
        await EnsureInitializedAsync(ct).ConfigureAwait(false);
        var codes = await Db.SetMembersAsync(ProvincesSetKey).ConfigureAwait(false);
        var list = new List<RegionInfoDto>();
        foreach (var rv in codes.Select(x => x.ToString()).OrderBy(x => x))
        {
            var hash = await Db.HashGetAllAsync(string.Format(ProvinceInfoKeyTpl, rv)).ConfigureAwait(false);
            var dto = ToRegion(hash);
            if (dto is not null)
                list.Add(dto);
        }
        return list;
    }

    public async Task<IReadOnlyList<RegionInfoDto>> GetCitiesAsync(string provinceCode, CancellationToken ct = default)
    {
        await EnsureInitializedAsync(ct).ConfigureAwait(false);
        if (!await Db.SetContainsAsync(ProvincesSetKey, provinceCode).ConfigureAwait(false))
            throw new KeyNotFoundException($"省份代码 {provinceCode} 不存在");

        var codes = await Db.SetMembersAsync(string.Format(ProvinceCitiesKeyTpl, provinceCode)).ConfigureAwait(false);
        var list = new List<RegionInfoDto>();
        foreach (var rv in codes.Select(x => x.ToString()).OrderBy(x => x))
        {
            var hash = await Db.HashGetAllAsync(string.Format(CityInfoKeyTpl, rv)).ConfigureAwait(false);
            var dto = ToRegion(hash);
            if (dto is not null)
                list.Add(dto);
        }
        return list;
    }

    public async Task<IReadOnlyList<RegionInfoDto>> GetDistrictsAsync(string cityCode, CancellationToken ct = default)
    {
        await EnsureInitializedAsync(ct).ConfigureAwait(false);
        var cityInfo = await Db.HashGetAllAsync(string.Format(CityInfoKeyTpl, cityCode)).ConfigureAwait(false);
        if (cityInfo.Length == 0)
            throw new KeyNotFoundException($"城市代码 {cityCode} 不存在");

        var codes = await Db.SetMembersAsync(string.Format(CityDistrictsKeyTpl, cityCode)).ConfigureAwait(false);
        var list = new List<RegionInfoDto>();
        foreach (var rv in codes.Select(x => x.ToString()).OrderBy(x => x))
        {
            var hash = await Db.HashGetAllAsync(string.Format(DistrictInfoKeyTpl, rv)).ConfigureAwait(false);
            var dto = ToRegion(hash);
            if (dto is not null)
                list.Add(dto);
        }
        return list;
    }

    private static RegionInfoDto? ToRegion(HashEntry[] hash)
    {
        string? code = null, name = null;
        foreach (var h in hash)
        {
            if (h.Name == "code") code = h.Value.ToString();
            if (h.Name == "name") name = h.Value.ToString();
        }
        if (code is null || name is null)
            return null;
        return new RegionInfoDto(code, name);
    }

    /// <summary>内嵌示例数据：学习用；真实项目可改为从静态 JSON 或官方数据源导入。</summary>
    private static (
        List<(string Code, string Name)> Provinces,
        Dictionary<string, List<(string Code, string Name)>> Cities,
        Dictionary<string, List<(string Code, string Name)>> Districts) SampleData()
    {
        var provinces = new List<(string, string)>
        {
            ("110000", "北京市"), ("120000", "天津市"), ("130000", "河北省"), ("310000", "上海市"),
            ("320000", "江苏省"), ("330000", "浙江省"), ("440000", "广东省")
        };
        var cities = new Dictionary<string, List<(string, string)>>
        {
            ["110000"] = [("110100", "北京市")],
            ["120000"] = [("120100", "天津市")],
            ["130000"] = [("130100", "石家庄市"), ("130200", "唐山市"), ("130300", "秦皇岛市")],
            ["310000"] = [("310100", "上海市")],
            ["320000"] = [("320100", "南京市"), ("320500", "苏州市"), ("320200", "无锡市")],
            ["330000"] = [("330100", "杭州市"), ("330200", "宁波市"), ("330300", "温州市")],
            ["440000"] = [("440100", "广州市"), ("440300", "深圳市"), ("440400", "珠海市")]
        };
        var districts = new Dictionary<string, List<(string, string)>>
        {
            ["110100"] = [("110101", "东城区"), ("110102", "西城区"), ("110105", "朝阳区"), ("110106", "丰台区")],
            ["320100"] = [("320102", "玄武区"), ("320104", "秦淮区"), ("320105", "建邺区"), ("320106", "鼓楼区")],
            ["330100"] = [("330102", "上城区"), ("330105", "拱墅区"), ("330106", "西湖区"), ("330108", "滨江区")],
            ["440100"] = [("440103", "荔湾区"), ("440104", "越秀区"), ("440105", "海珠区"), ("440106", "天河区")]
        };
        return (provinces, cities, districts);
    }
}

/// <summary>返回给前端的省/市/区一项。</summary>
public record RegionInfoDto(string Code, string Name);
