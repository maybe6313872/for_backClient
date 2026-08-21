package com.zhiliao.ainame.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AuthDtos {
    private AuthDtos() {
    }

    public record RegisterRequest(
        @NotBlank @Email String email,
        @NotBlank @Size(min = 3, max = 20) String username,
        @NotBlank @Size(min = 6, max = 20) String password,
        @NotBlank @Size(min = 6, max = 20) String confirmPassword,
        @NotBlank @Size(min = 4, max = 4) String code
    ) {
    }

    public record LoginRequest(
        @NotBlank @Email String email,
        @NotBlank @Size(min = 6, max = 20) String password
    ) {
    }

    public record UserDto(Integer id, String email, String username) {
    }

    public record LoginResponse(UserDto user, String token) {
    }
}
