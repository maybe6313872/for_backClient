package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.dto.AuthDtos.LoginRequest;
import com.zhiliao.ainame.dto.AuthDtos.LoginResponse;
import com.zhiliao.ainame.dto.AuthDtos.RegisterRequest;
import com.zhiliao.ainame.dto.AuthDtos.UserDto;
import com.zhiliao.ainame.dto.CommonDtos.ResponseOut;
import com.zhiliao.ainame.entity.AppUser;
import com.zhiliao.ainame.entity.EmailCode;
import com.zhiliao.ainame.repository.AppUserRepository;
import com.zhiliao.ainame.repository.EmailCodeRepository;
import com.zhiliao.ainame.service.EmailSender;
import com.zhiliao.ainame.service.JwtTokenService;
import jakarta.validation.Valid;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
public class AuthController {
    private final AppUserRepository users;
    private final EmailCodeRepository emailCodes;
    private final EmailSender emailSender;
    private final JwtTokenService jwtTokenService;
    private final PasswordEncoder passwordEncoder;

    public AuthController(
        AppUserRepository users,
        EmailCodeRepository emailCodes,
        EmailSender emailSender,
        JwtTokenService jwtTokenService,
        PasswordEncoder passwordEncoder
    ) {
        this.users = users;
        this.emailCodes = emailCodes;
        this.emailSender = emailSender;
        this.jwtTokenService = jwtTokenService;
        this.passwordEncoder = passwordEncoder;
    }

    @GetMapping("/code")
    public ResponseEntity<?> getEmailCode(@RequestParam("email") String email) {
        if (email == null || email.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("detail", "邮箱不能为空"));
        }

        String code = "%04d".formatted(ThreadLocalRandom.current().nextInt(0, 10000));
        emailSender.sendPlain(email, "【知了课堂】注册验证码", "您的验证码为：" + code + "，五分钟有效！");

        var row = new EmailCode();
        row.setEmail(email);
        row.setCode(code);
        row.setType("test");
        row.setCreatedTime(LocalDateTime.now());
        emailCodes.save(row);
        return ResponseEntity.ok(new ResponseOut());
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest data) {
        if (!data.password().equals(data.confirmPassword())) {
            return ResponseEntity.badRequest().body(Map.of("detail", "两个密码不一致！"));
        }
        if (users.existsByEmail(data.email())) {
            return ResponseEntity.badRequest().body(Map.of("detail", "该邮箱已经存在！"));
        }
        if (!isEmailCodeValid(data.email(), data.code())) {
            return ResponseEntity.badRequest().body(Map.of("detail", "邮箱或验证码错误！"));
        }

        var user = new AppUser();
        user.setEmail(data.email());
        user.setUsername(data.username());
        user.setPasswordHash(passwordEncoder.encode(data.password()));
        users.save(user);
        return ResponseEntity.ok(new ResponseOut());
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest data) {
        var user = users.findByEmail(data.email()).orElse(null);
        if (user == null) {
            return ResponseEntity.badRequest().body(Map.of("detail", "该用户不存在！"));
        }
        if (!passwordEncoder.matches(data.password(), user.getPasswordHash())) {
            return ResponseEntity.badRequest().body(Map.of("detail", "邮箱或密码错误！"));
        }

        var tokens = jwtTokenService.createLoginTokens(user.getId());
        return ResponseEntity.ok(new LoginResponse(
            new UserDto(user.getId(), user.getEmail(), user.getUsername()),
            tokens.accessToken()
        ));
    }

    private boolean isEmailCodeValid(String email, String code) {
        return emailCodes.findFirstByEmailAndCodeOrderByIdDesc(email, code)
            .filter(row -> Duration.between(row.getCreatedTime(), LocalDateTime.now()).toMinutes() <= 10)
            .isPresent();
    }
}
