"""
邮件服务配置模块

本模块提供了邮件服务的配置和实例创建功能。
使用 fastapi-mail 库实现异步邮件发送。
"""

from fastapi_mail import FastMail, ConnectionConfig
from pydantic import SecretStr, EmailStr
import settings


def create_mail_instance() -> FastMail:
    """
    创建 FastMail 实例
    
    根据配置创建并返回一个 FastMail 实例，用于发送邮件。
    每次调用都会创建新实例，确保线程/协程安全。
    
    Returns:
        FastMail: 配置好的邮件服务实例
        
    Note:
        - 邮件配置从 settings 模块读取
        - 使用 STARTTLS 加密连接（MAIL_STARTTLS=True）
        - 启用证书验证（VALIDATE_CERTS=True）
        - 密码使用 SecretStr 类型保护，避免日志泄露
        
    Configuration:
        - MAIL_USERNAME: SMTP 服务器用户名
        - MAIL_PASSWORD: SMTP 服务器密码（或授权码）
        - MAIL_FROM: 发件人邮箱地址
        - MAIL_PORT: SMTP 服务器端口（通常为 587）
        - MAIL_SERVER: SMTP 服务器地址
        - MAIL_FROM_NAME: 发件人显示名称
        - MAIL_STARTTLS: 是否使用 STARTTLS 加密
        - MAIL_SSL_TLS: 是否使用 SSL/TLS 加密
    """
    # 创建邮件连接配置
    mail_config = ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,                    # SMTP 用户名
        MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),         # SMTP 密码（使用 SecretStr 保护）
        MAIL_FROM=settings.MAIL_FROM,                            # 发件人邮箱
        MAIL_PORT=settings.MAIL_PORT,                            # SMTP 端口
        MAIL_SERVER=settings.MAIL_SERVER,                        # SMTP 服务器地址
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,                 # 发件人显示名称
        MAIL_STARTTLS=settings.MAIL_STARTTLS,                    # 启用 STARTTLS
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,                      # SSL/TLS 设置
        USE_CREDENTIALS=True,                                    # 使用认证信息
        VALIDATE_CERTS=True,                                     # 验证 SSL 证书
    )
    
    # 创建并返回 FastMail 实例
    return FastMail(mail_config)