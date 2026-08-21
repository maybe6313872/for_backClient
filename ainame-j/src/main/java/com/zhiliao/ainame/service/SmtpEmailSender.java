package com.zhiliao.ainame.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Service
public class SmtpEmailSender implements EmailSender {
    private final JavaMailSender mailSender;
    private final String username;
    private final String from;
    private final String fromName;

    public SmtpEmailSender(
        JavaMailSender mailSender,
        @Value("${spring.mail.username:}") String username,
        @Value("${app.mail.from:}") String from,
        @Value("${app.mail.from-name:知了课堂}") String fromName
    ) {
        this.mailSender = mailSender;
        this.username = username;
        this.from = from;
        this.fromName = fromName;
    }

    @Override
    public void sendPlain(String to, String subject, String body) {
        if (!StringUtils.hasText(username)) {
            throw new IllegalStateException("请在配置中设置 spring.mail.username 与 spring.mail.password。");
        }

        var message = new SimpleMailMessage();
        message.setFrom(StringUtils.hasText(from) ? from : username);
        message.setTo(to);
        message.setSubject(subject);
        message.setText(body);
        mailSender.send(message);
    }

    public String fromName() {
        return fromName;
    }
}
