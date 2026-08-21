package com.zhiliao.ainame.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;
import java.util.List;

public final class OrderDtos {
    private OrderDtos() {
    }

    public record CompanyCreateInDto(@NotBlank @Size(max = 100) String name, @NotBlank @Size(max = 200) String address) {
    }

    public record CompanyUpdateInDto(@NotNull Integer id, @NotBlank @Size(max = 100) String name, @NotBlank @Size(max = 200) String address) {
    }

    public record CompanyOutDto(Integer id, String name, String address, LocalDateTime createdTime) {
    }

    public record ProductInDto(
        Integer id,
        @NotBlank @Size(max = 100) String name,
        @NotNull Float price,
        @NotNull Integer storenum,
        @NotBlank @Size(max = 200) String description,
        @NotBlank @Size(max = 200) String productno
    ) {
    }

    public record ProductOutDto(Integer id, String name, Float price, Integer storenum, String description, String productno, LocalDateTime createdTime) {
    }

    public record OrderLineItemDto(@JsonProperty("id") Integer id, @JsonProperty("number") Float number) {
    }

    public record OrderInDto(Integer id, @NotBlank @Size(max = 100) String orderNumber, @NotNull Integer companyId, @NotEmpty List<OrderLineItemDto> productList) {
    }

    public record OrderProductRowOutDto(Integer productId, String productName, Float number, Float price) {
    }

    public record OrderQueryRowOutDto(
        Integer id,
        String orderNumber,
        Integer companyId,
        String companyName,
        List<OrderProductRowOutDto> productList,
        Float totalPrice
    ) {
    }

    public record OrderQueryApiResponseDto(int code, List<OrderQueryRowOutDto> data, @JsonProperty("msg") String msg) {
        public OrderQueryApiResponseDto(List<OrderQueryRowOutDto> data) {
            this(200, data, "success");
        }
    }
}
