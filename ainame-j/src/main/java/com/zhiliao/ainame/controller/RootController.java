package com.zhiliao.ainame.controller;

import com.zhiliao.ainame.service.EmailSender;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.util.StringUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RootController {
    private final EmailSender emailSender;

    public RootController(EmailSender emailSender) {
        this.emailSender = emailSender;
    }

    @GetMapping("/")
    public Map<String, String> root() {
        return Map.of("message", "Hello World");
    }

    @GetMapping("/hello/{name}")
    public Map<String, String> hello(@org.springframework.web.bind.annotation.PathVariable("name") String name) {
        return Map.of("message", "Hello " + name);
    }

    @GetMapping("/mail/test")
    public ResponseEntity<?> mailTest(@RequestParam("email") String email) {
        if (!StringUtils.hasText(email)) {
            return ResponseEntity.badRequest().body(Map.of("detail", "email 查询参数必填"));
        }
        emailSender.sendPlain(email, "hello", "hello " + email);
        return ResponseEntity.ok(Map.of("message", "邮件发送成功！"));
    }
}
