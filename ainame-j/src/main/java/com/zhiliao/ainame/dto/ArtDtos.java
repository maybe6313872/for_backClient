package com.zhiliao.ainame.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.util.List;

public final class ArtDtos {
    private ArtDtos() {
    }

    public record ArtDeleteIn(@NotEmpty List<Integer> idArr) {
    }

    public record ArtChangeIn(@NotNull Integer id, @NotBlank @Size(max = 10) String sex) {
    }

    public record ArtQueryIn(
        @Min(1) Integer page,
        @Min(1) @Max(100) Integer size,
        @NotBlank @Size(max = 10) String sex
    ) {
        public int pageOrDefault() {
            return page == null ? 1 : page;
        }

        public int sizeOrDefault() {
            return size == null ? 10 : size;
        }
    }

    public record ArtOutDto(Integer id, String username, String sex, String artcontent) {
    }

    public record ArtQueryOutDto(int code, String message, Object data) {
        public ArtQueryOutDto(Object data) {
            this(200, "查询成功", data);
        }
    }
}
