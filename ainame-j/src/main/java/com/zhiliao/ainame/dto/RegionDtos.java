package com.zhiliao.ainame.dto;

import java.util.List;

public final class RegionDtos {
    private RegionDtos() {
    }

    public record RegionItemDto(String code, String name) {
    }

    public record RegionListResponseDto(int code, String message, List<RegionItemDto> data) {
    }
}
