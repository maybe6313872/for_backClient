# Docker 部署指南

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+（如果使用 docker-compose）

## 快速开始

### 方式一：使用 Docker Compose（推荐）

1. **创建环境变量文件**（可选）

   创建 `.env` 文件，配置敏感信息：

   ```env
   # 数据库配置
   DB_URI=ainame://root:your_password@mysql:3306/zhiliao_ainame?charset=utf8mb4
   MYSQL_ROOT_PASSWORD=your_password
   MYSQL_DATABASE=zhiliao_ainame

   # 邮件配置
   MAIL_USERNAME=your_email@qq.com
   MAIL_PASSWORD=your_email_auth_code
   MAIL_FROM=your_email@qq.com

   # JWT 配置
   JWT_SECRET_KEY=your_secret_key_here

   # 是否自动运行数据库迁移
   RUN_MIGRATIONS=true
   ```

2. **构建并启动服务**

   ```bash
   docker-compose up -d
   ```

3. **查看日志**

   ```bash
   docker-compose logs -f app
   ```

4. **停止服务**

   ```bash
   docker-compose down
   ```

### 方式二：使用 Docker 命令

1. **构建镜像**

   ```bash
   docker build -t zhiliao-ainame:latest .
   ```

2. **运行容器**

   ```bash
   docker run -d \
     --name zhiliao-ainame \
     -p 8000:8000 \
     -e DB_URI="ainame://root:password@host.docker.internal:3306/zhiliao_ainame?charset=utf8mb4" \
     -e MAIL_USERNAME="your_email@qq.com" \
     -e MAIL_PASSWORD="your_auth_code" \
     -e JWT_SECRET_KEY="your_secret_key" \
     zhiliao-ainame:latest
   ```

3. **查看日志**

   ```bash
   docker logs -f zhiliao-ainame
   ```

## 数据库迁移

### 方式一：在容器启动前运行迁移

```bash
# 进入容器
docker exec -it zhiliao-ainame-app bash

# 运行迁移
alembic upgrade head
```

### 方式二：自动运行迁移

设置环境变量 `RUN_MIGRATIONS=true`，容器启动时会自动运行迁移。

### 方式三：使用单独的迁移容器

```bash
docker run --rm \
  --network zhiliao-ainame_app-network \
  -e DB_URI="ainame://root:password@mysql:3306/zhiliao_ainame?charset=utf8mb4" \
  zhiliao-ainame:latest \
  alembic upgrade head
```

## 环境变量说明

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `DB_URI` | 数据库连接URI | `ainame://root:root@mysql:3306/zhiliao_ainame?charset=utf8mb4` | 是 |
| `MAIL_USERNAME` | 邮件服务器用户名 | `360999519@qq.com` | 否 |
| `MAIL_PASSWORD` | 邮件服务器密码/授权码 | - | 是（如果使用邮件功能） |
| `MAIL_FROM` | 发件人邮箱 | `360999519@qq.com` | 否 |
| `MAIL_SERVER` | SMTP服务器地址 | `smtp.qq.com` | 否 |
| `MAIL_PORT` | SMTP端口 | `587` | 否 |
| `JWT_SECRET_KEY` | JWT签名密钥 | `sfsadadafsjw` | 是（生产环境必须修改） |
| `RUN_MIGRATIONS` | 是否自动运行迁移 | `false` | 否 |

## 生产环境部署建议

1. **使用环境变量管理敏感信息**
   - 不要将密码硬编码在代码中
   - 使用 Docker secrets 或外部密钥管理服务

2. **配置反向代理**
   - 使用 Nginx 或 Traefik 作为反向代理
   - 配置 SSL/TLS 证书

3. **数据持久化**
   - MySQL 数据使用 Docker volume
   - 日志文件挂载到宿主机

4. **监控和日志**
   - 配置日志收集（如 ELK、Loki）
   - 设置健康检查
   - 配置监控告警

5. **安全加固**
   - 使用非 root 用户运行（Dockerfile 已配置）
   - 限制容器资源使用
   - 定期更新基础镜像和依赖

## 常用命令

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs -f zhiliao-ainame-app

# 进入容器
docker exec -it zhiliao-ainame-app bash

# 重启服务
docker-compose restart app

# 更新镜像并重启
docker-compose pull
docker-compose up -d

# 清理未使用的镜像和容器
docker system prune -a
```

## 故障排查

### 容器无法启动

1. 查看日志：`docker logs zhiliao-ainame-app`
2. 检查端口是否被占用：`netstat -tuln | grep 8000`
3. 检查数据库连接是否正常

### 数据库连接失败

1. 确认数据库服务已启动
2. 检查 `DB_URI` 环境变量是否正确
3. 确认网络连接（如果使用外部数据库）

### 迁移失败

1. 确认数据库已创建
2. 检查数据库用户权限
3. 查看迁移日志：`docker logs zhiliao-ainame-app`
