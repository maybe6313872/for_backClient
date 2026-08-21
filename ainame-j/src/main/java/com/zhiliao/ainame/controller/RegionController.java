package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.RegionDtos.RegionListResponseDto;
import com.zhiliao.ainame.service.RegionDataService;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/region")
public class RegionController {
    private final RegionDataService regionDataService;

    public RegionController(RegionDataService regionDataService) {
        this.regionDataService = regionDataService;
    }

    @GetMapping("/provinces")
    public RegionListResponseDto provinces() {
        var data = regionDataService.getProvinces();
        return new RegionListResponseDto(200, data.isEmpty() ? "暂无数据" : "查询成功", data);
    }

    @GetMapping("/cities")
    public ResponseEntity<?> cities(@RequestParam("province_code") String provinceCode) {
        try {
            var data = regionDataService.getCities(provinceCode);
            return ResponseEntity.ok(new RegionListResponseDto(200, data.isEmpty() ? "该省份暂无城市数据" : "查询成功", data));
        } catch (IllegalArgumentException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", ex.getMessage()));
        }
    }

    @GetMapping("/districts")
    public ResponseEntity<?> districts(@RequestParam("city_code") String cityCode) {
        try {
            var data = regionDataService.getDistricts(cityCode);
            return ResponseEntity.ok(new RegionListResponseDto(200, data.isEmpty() ? "该城市暂无区县数据" : "查询成功", data));
        } catch (IllegalArgumentException ex) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("detail", ex.getMessage()));
        }
    }

    @PostMapping("/init")
    public Map<String, Object> init() {
        regionDataService.ensureInitialized();
        return Map.of("code", 200, "message", "省市区数据初始化成功");
    }
}
