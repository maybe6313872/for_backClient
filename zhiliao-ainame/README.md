# 知了AI起名 API

一个基于 FastAPI 和 AI 的智能起名服务 API，提供用户注册、登录和智能起名功能。

## 项目简介

本项目是一个 RESTful API 服务，主要功能包括：
- 用户注册和登录（基于邮箱验证码）
- JWT 身份认证
- 基于 AI 的智能起名服务
- 邮件发送功能

## 技术栈

- **Web 框架**: FastAPI
- **数据库**: MySQL (使用 SQLAlchemy ORM)
- **异步支持**: SQLAlchemy Async + aiomysql
- **身份认证**: JWT (PyJWT)
- **密码加密**: pwdlib (Argon2)
- **邮件服务**: fastapi-mail
- **AI 服务**: LangChain + DeepSeek
- **数据库迁移**: Alembic
- **API 文档**: Swagger UI / ReDoc

## 项目结构

```
zhiliao-ainame/
├── alembic/                  # 数据库迁移文件
│   ├── versions/             # 迁移版本文件
│   └── env.py                # Alembic 环境配置
├── core/                     # 核心功能模块
│   ├── agent.py             # AI 起名代理
│   ├── auth.py              # JWT 认证处理
│   └── mail.py              # 邮件服务配置
├── models/                   # 数据库模型
│   ├── __init__.py          # SQLAlchemy 配置
│   └── user.py              # 用户模型
├── repository/               # 数据访问层
│   └── user_repo.py         # 用户数据仓库
├── routers/                  # API 路由
│   ├── auth_router.py       # 认证相关路由（注册、登录、验证码）
│   └── name_router.py       # 起名相关路由
├── schemas/                  # Pydantic 数据模型
│   ├── agent.py             # AI 相关模型
│   ├── name.py              # 起名相关模型
│   ├── user.py              # 用户相关模型
│   └── __init__.py          # 通用响应模型
├── settings/                  # 配置模块
│   └── __init__.py          # 数据库、邮件、JWT 配置
├── dependencies.py           # FastAPI 依赖注入
├── main.py                   # 应用入口文件
├── requirements.txt          # Python 依赖列表
├── alembic.ini              # Alembic 配置文件
├── generate_swagger.py      # Swagger 文档生成脚本
├── test_swagger.py          # Swagger 测试脚本
└── openapi.json             # OpenAPI 规范文件（自动生成）
```

## 环境要求

- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+
- 虚拟环境（推荐使用 venv）

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd zhiliao-ainame
```

### 2. 创建虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

1. 创建 MySQL 数据库：
```sql
CREATE DATABASE zhiliao_ainame CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 修改数据库配置（`settings/__init__.py`）：
```python
DB_URI = "mysql+aiomysql://用户名:密码@127.0.0.1:3306/zhiliao_ainame?charset=utf8mb4"
```

3. 运行数据库迁移：
```bash
alembic upgrade head
```

### 5. 配置邮件服务（可选）

如果需要使用邮件功能，请在 `settings/__init__.py` 中配置邮件服务器信息：

```python
MAIL_USERNAME = "your_email@example.com"
MAIL_PASSWORD = "your_email_password"
MAIL_FROM = "your_email@example.com"
MAIL_PORT = 587
MAIL_SERVER = "smtp.example.com"
MAIL_FROM_NAME = "知了课堂"
MAIL_STARTTLS = True
MAIL_SSL_TLS = False
```

### 6. 配置 JWT 密钥（可选）

在 `settings/__init__.py` 中修改 JWT 密钥：

```python
JWT_SECRET_KEY = "your-secret-key-here"
```

## 启动服务

### 开发模式（推荐）

```bash
uvicorn main:app --reload
```

### 生产模式

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 使用 Python 模块方式启动

```bash
python -m uvicorn main:app --reload
```

服务启动后，访问以下地址：

- **API 文档 (Swagger UI)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **API 根路径**: http://localhost:8000/

## API 端点

### 认证相关 (`/auth`)

- `GET /auth/code` - 获取邮箱验证码
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录

### 起名相关 (`/name`)

- `POST /name/` - 生成名字（需要认证）

### 其他

- `GET /` - 根路径
- `GET /hello/{name}` - 问候接口
- `GET /mail/test` - 邮件测试接口

## 使用示例

### 1. 获取验证码

```bash
curl "http://localhost:8000/auth/code?email=user@example.com"
```

### 2. 用户注册

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "confirm_password": "password123",
    "code": "1234"
  }'
```

### 3. 用户登录

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 4. 生成名字（需要认证）

```bash
curl -X POST "http://localhost:8000/name/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "surname": "张",
    "gender": "男",
    "length": "两字",
    "other": "希望名字有文化内涵",
    "exclude": []
  }'
```

## 生成 Swagger 文档

项目包含自动生成 Swagger 文档的脚本：

```bash
python generate_swagger.py
```

这将生成 `openapi.json` 和 `openapi.yaml` 文件。

## 数据库迁移

### 创建新的迁移

```bash
alembic revision --autogenerate -m "描述信息"
```

### 应用迁移

```bash
alembic upgrade head
```

### 回滚迁移

```bash
alembic downgrade -1
```

## 依赖说明

主要依赖包及其用途：

- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `sqlalchemy` - ORM 框架
- `aiomysql` - 异步 MySQL 驱动
- `alembic` - 数据库迁移工具
- `pydantic` - 数据验证
- `PyJWT` - JWT 令牌处理
- `pwdlib[argon2]` - 密码加密
- `fastapi-mail` - 邮件发送
- `langchain` / `langchain-deepseek` - AI 服务集成
- `PyYAML` - YAML 文件处理

完整依赖列表请查看 `requirements.txt`。

## 开发建议

1. **使用虚拟环境**: 始终在虚拟环境中开发和运行项目
2. **环境变量**: 生产环境建议使用环境变量管理敏感配置
3. **日志记录**: 可以添加日志记录功能以便调试和监控
4. **错误处理**: 完善错误处理机制
5. **测试**: 添加单元测试和集成测试

## 常见问题

### Swagger 文档不显示

请参考 `SWAGGER_TROUBLESHOOTING.md` 文件进行排查。

### 数据库连接失败

1. 检查 MySQL 服务是否启动
2. 确认数据库配置信息正确
3. 检查数据库用户权限

### 邮件发送失败

1. 检查邮件服务器配置
2. 确认邮箱密码/授权码正确
3. 检查网络连接和防火墙设置

## 许可证

[添加许可证信息]

## 联系方式

[添加联系方式]
