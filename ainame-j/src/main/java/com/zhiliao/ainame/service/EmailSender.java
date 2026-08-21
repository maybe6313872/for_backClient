package com.zhiliao.ainame.service;

public interface EmailSender {
    void sendPlain(String to, String subject, String body);
}
