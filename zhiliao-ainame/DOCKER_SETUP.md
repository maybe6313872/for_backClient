# Docker 安装和构建指南

## 1. 安装 Docker

### Windows 系统

1. **下载 Docker Desktop**
   - 访问：https://www.docker.com/products/docker-desktop
   - 下载 Windows 版本并安装
   - 安装完成后重启电脑

2. **启动 Docker Desktop**
   - 启动后等待 Docker 引擎启动完成
   - 系统托盘会显示 Docker 图标

3. **验证安装**
   ```powershell
   docker --version
   docker-compose --version
   ```

### Linux 系统（Ubuntu/Debian）

```bash
# 更新包索引
sudo apt-get update

# 安装 Docker
sudo apt-get install -y docker.io docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到 docker 组（可选，避免每次都用 sudo）
sudo usermod -aG docker $USER

# 验证安装
docker --version
docker-compose --version
```

### Linux 系统（CentOS/RHEL）

```bash
# 安装 Docker
sudo yum install -y docker docker-compose

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker-compose --version
```

## 2. 构建镜像

### 方式一：使用构建脚本（推荐）

**Windows:**
```powershell
.\build-docker.bat
```

**Linux/Mac:**
```bash
chmod +x build-docker.sh
./build-docker.sh
```

### 方式二：使用 Docker 命令

```bash
docker build -t zhiliao-ainame:latest .
```

### 方式三：使用 Docker Compose

```bash
docker-compose build
```

## 3. 运行容器

### 方式一：使用 Docker Compose（推荐）

1. **创建 `.env` 文件**（可选，用于配置环境变量）

   ```env
   DB_URI=ainame://root:your_password@mysql:3306/zhiliao_ainame?charset=utf8mb4
   MYSQL_ROOT_PASSWORD=your_password
   MAIL_PASSWORD=your_email_auth_code
   JWT_SECRET_KEY=your_secret_key
   RUN_MIGRATIONS=true
   ```

2. **启动服务**

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

### 方式二：单独运行容器

```bash
docker run -d \
  --name zhiliao-ainame \
  -p 8000:8000 \
  -e DB_URI="ainame://root:password@your_db_host:3306/zhiliao_ainame?charset=utf8mb4" \
  -e MAIL_PASSWORD="your_email_auth_code" \
  -e JWT_SECRET_KEY="your_secret_key" \
  zhiliao-ainame:latest
```

## 4. 验证部署

1. **检查容器状态**
   ```bash
   docker ps
   ```

2. **访问 API**
   - API 文档：http://localhost:8000/docs
   - 健康检查：http://localhost:8000/

3. **查看日志**
   ```bash
   docker logs -f zhiliao-ainame
   ```

## 5. 常见问题

### 问题1：Docker 命令找不到

**解决方案：**
- Windows: 确保 Docker Desktop 已启动
- Linux: 检查 Docker 服务是否运行：`sudo systemctl status docker`

### 问题2：端口被占用

**解决方案：**
```bash
# Windows 检查端口占用
netstat -ano | findstr :8000

# Linux 检查端口占用
sudo lsof -i :8000

# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 改为其他端口
```

### 问题3：数据库连接失败

**解决方案：**
- 检查 `DB_URI` 环境变量是否正确
- 确认数据库服务已启动
- 如果使用外部数据库，确保网络连通

### 问题4：构建失败

**解决方案：**
- 检查 Dockerfile 语法
- 查看详细错误信息：`docker build --no-cache -t zhiliao-ainame:latest .`
- 确保所有依赖文件存在

## 6. 生产环境部署

### 在服务器上部署

1. **上传项目文件到服务器**
   ```bash
   scp -r . user@server:/path/to/project
   ```

2. **SSH 连接到服务器**
   ```bash
   ssh user@server
   cd /path/to/project
   ```

3. **构建并启动**
   ```bash
   docker-compose up -d --build
   ```

4. **配置反向代理（Nginx）**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## 7. 镜像导出和导入

### 导出镜像（用于离线部署）

```bash
# 导出镜像
docker save zhiliao-ainame:latest -o zhiliao-ainame.tar

# 在目标服务器导入
docker load -i zhiliao-ainame.tar
```

## 8. 清理资源

```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi zhiliao-ainame:latest

# 清理未使用的资源
docker system prune -a
```
