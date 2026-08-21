"""
应用配置模块

本模块包含应用的所有配置信息，包括：
- 数据库连接配置
- 邮件服务配置
- JWT 认证配置

注意：生产环境建议使用环境变量管理敏感配置信息。
"""

import os
from datetime import timedelta


# ==================== 数据库配置 ====================
# MySQL 数据库连接 URI
# 格式：ainame://用户名:密码@主机:端口/数据库名?charset=字符集
# 注意：生产环境应使用环境变量，不要硬编码密码
# 优先从环境变量读取，如果没有则使用默认值
DB_URI = os.getenv(
    "DB_URI",
    "ainame://root:root@127.0.0.1:3306/zhiliao_ainame?charset=utf8mb4"
)
DB_URI_TEST = os.getenv(
    "DB_URI_TEST",
    DB_URI  # 默认使用 DB_URI 的值
)


# ==================== 邮件服务配置 ====================
# SMTP 服务器配置
# 用于发送邮箱验证码等邮件
# 优先从环境变量读取，如果没有则使用默认值

# SMTP 服务器用户名（通常是邮箱地址）
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "360999519@qq.com")

# SMTP 服务器密码（QQ邮箱需要使用授权码，不是登录密码）
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "honvtfvjsfaybijf")

# 发件人邮箱地址
MAIL_FROM = os.getenv("MAIL_FROM", "360999519@qq.com")

# SMTP 服务器端口（QQ邮箱使用587端口）
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))

# SMTP 服务器地址（QQ邮箱的SMTP服务器）
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.qq.com")

# 发件人显示名称
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "知了课堂")

# 是否使用 STARTTLS 加密（QQ邮箱需要启用）
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "true").lower() == "true"

# 是否使用 SSL/TLS 加密（QQ邮箱使用 STARTTLS，不使用 SSL）
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "false").lower() == "true"


# ==================== JWT 认证配置 ====================
# JWT 令牌相关配置

# JWT 签名密钥
# 注意：生产环境必须使用强随机密钥，不要使用默认值
# 建议使用环境变量或密钥管理服务
# 优先从环境变量读取，如果没有则使用默认值（生产环境必须设置）
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sfsadadafsjw")

# 访问令牌有效期（15天）
# 用于 API 请求的身份验证
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=15)

# 刷新令牌有效期（30天）
# 用于刷新访问令牌
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

