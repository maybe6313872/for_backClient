package com.zhiliao.ainame.service;

import com.zhiliao.ainame.dto.RegionDtos.RegionItemDto;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class RegionDataService {
    private static final String PROVINCES_SET_KEY = "region:provinces:set";
    private static final String PROVINCE_INFO_KEY = "region:province:%s:info";
    private static final String PROVINCE_CITIES_KEY = "region:province:%s:cities:set";
    private static final String CITY_INFO_KEY = "region:city:%s:info";
    private static final String CITY_DISTRICTS_KEY = "region:city:%s:districts:set";
    private static final String DISTRICT_INFO_KEY = "region:district:%s:info";

    private final StringRedisTemplate redis;

    public RegionDataService(StringRedisTemplate redis) {
        this.redis = redis;
    }

    public void ensureInitialized() {
        Boolean exists = redis.hasKey(PROVINCES_SET_KEY);
        if (Boolean.TRUE.equals(exists)) {
            return;
        }

        sampleProvinces().forEach((code, name) -> {
            redis.opsForSet().add(PROVINCES_SET_KEY, code);
            putRegion(String.format(PROVINCE_INFO_KEY, code), code, name);
        });

        sampleCities().forEach((provinceCode, cities) -> cities.forEach((code, name) -> {
            putRegion(String.format(CITY_INFO_KEY, code), code, name);
            redis.opsForSet().add(String.format(PROVINCE_CITIES_KEY, provinceCode), code);
        }));

        sampleDistricts().forEach((cityCode, districts) -> districts.forEach((code, name) -> {
            putRegion(String.format(DISTRICT_INFO_KEY, code), code, name);
            redis.opsForSet().add(String.format(CITY_DISTRICTS_KEY, cityCode), code);
        }));
    }

    public List<RegionItemDto> getProvinces() {
        ensureInitialized();
        return readSet(PROVINCES_SET_KEY, PROVINCE_INFO_KEY);
    }

    public List<RegionItemDto> getCities(String provinceCode) {
        ensureInitialized();
        if (Boolean.FALSE.equals(redis.opsForSet().isMember(PROVINCES_SET_KEY, provinceCode))) {
            throw new IllegalArgumentException("省份代码 " + provinceCode + " 不存在");
        }
        return readSet(String.format(PROVINCE_CITIES_KEY, provinceCode), CITY_INFO_KEY);
    }

    public List<RegionItemDto> getDistricts(String cityCode) {
        ensureInitialized();
        if (redis.opsForHash().size(String.format(CITY_INFO_KEY, cityCode)) == 0) {
            throw new IllegalArgumentException("城市代码 " + cityCode + " 不存在");
        }
        return readSet(String.format(CITY_DISTRICTS_KEY, cityCode), DISTRICT_INFO_KEY);
    }

    private void putRegion(String key, String code, String name) {
        redis.opsForHash().put(key, "code", code);
        redis.opsForHash().put(key, "name", name);
    }

    private List<RegionItemDto> readSet(String setKey, String infoKeyTemplate) {
        var codes = redis.opsForSet().members(setKey);
        if (codes == null || codes.isEmpty()) {
            return List.of();
        }

        var result = new ArrayList<RegionItemDto>();
        codes.stream().sorted().forEach(code -> {
            var key = String.format(infoKeyTemplate, code);
            Object name = redis.opsForHash().get(key, "name");
            if (name != null) {
                result.add(new RegionItemDto(code, name.toString()));
            }
        });
        result.sort(Comparator.comparing(RegionItemDto::code));
        return result;
    }

    private static Map<String, String> sampleProvinces() {
        var provinces = new LinkedHashMap<String, String>();
        provinces.put("110000", "北京市");
        provinces.put("120000", "天津市");
        provinces.put("130000", "河北省");
        provinces.put("310000", "上海市");
        provinces.put("320000", "江苏省");
        provinces.put("330000", "浙江省");
        provinces.put("440000", "广东省");
        return provinces;
    }

    private static Map<String, Map<String, String>> sampleCities() {
        return Map.of(
            "110000", Map.of("110100", "北京市"),
            "120000", Map.of("120100", "天津市"),
            "130000", Map.of("130100", "石家庄市", "130200", "唐山市", "130300", "秦皇岛市"),
            "310000", Map.of("310100", "上海市"),
            "320000", Map.of("320100", "南京市", "320500", "苏州市", "320200", "无锡市"),
            "330000", Map.of("330100", "杭州市", "330200", "宁波市", "330300", "温州市"),
            "440000", Map.of("440100", "广州市", "440300", "深圳市", "440400", "珠海市")
        );
    }

    private static Map<String, Map<String, String>> sampleDistricts() {
        return Map.of(
            "110100", Map.of("110101", "东城区", "110102", "西城区", "110105", "朝阳区", "110106", "丰台区"),
            "320100", Map.of("320102", "玄武区", "320104", "秦淮区", "320105", "建邺区", "320106", "鼓楼区"),
            "330100", Map.of("330102", "上城区", "330105", "拱墅区", "330106", "西湖区", "330108", "滨江区"),
            "440100", Map.of("440103", "荔湾区", "440104", "越秀区", "440105", "海珠区", "440106", "天河区")
        );
    }
}
