package com.zhiliao.ainame.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import java.util.List;

public final class NameDtos {
    private NameDtos() {
    }

    public record NameRequest(
        @NotBlank String surname,
        @NotBlank @Pattern(regexp = "^(不限|男|女)$") String gender,
        @NotBlank @Pattern(regexp = "^(不限|单字|两字)$") String length,
        String other,
        List<String> exclude
    ) {
    }

    public record NameItemDto(String name, String reference, String moral) {
    }

    public record NameResponse(List<NameItemDto> names) {
    }
}
