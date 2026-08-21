# Nginx 前端部署指南

## 快速开始

### 1. 构建前端应用
```bash
npm run build
```
打包后的文件会生成在 `dist` 目录中。

### 2. 安装 Nginx

**Windows:**
```bash
# 下载并安装 Nginx
# 或使用 Chocolatey
choco install nginx
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install nginx
```

**macOS:**
```bash
brew install nginx
```

### 3. 配置 Nginx

#### 选项 A：复制配置文件
```bash
# Linux/macOS
sudo cp nginx.conf /etc/nginx/sites-available/default
sudo nginx -t  # 测试配置
sudo systemctl restart nginx

# Windows
# 将 nginx.conf 的内容复制到 Nginx 安装目录的 conf/nginx.conf
```

#### 选项 B：手动配置

编辑 Nginx 主配置文件，添加以下服务器块：

```nginx
server {
    listen 80;
    server_name localhost;
    
    # 根路径指向 dist 目录
    root /path/to/your/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 4. 启动 Nginx

```bash
# Linux/macOS
sudo systemctl start nginx
sudo systemctl enable nginx  # 开机自启

# Windows (在 cmd 中)
cd C:\nginx
start nginx

# 或使用 WSL
wsl sudo systemctl start nginx
```

### 5. 验证部署

访问 http://localhost，应该能看到你的前端应用。

---

## 配置说明

### 核心配置项

| 配置项 | 说明 |
|-------|------|
| `root` | 指定静态文件根目录（dist 目录所在路径） |
| `try_files $uri $uri/ /index.html` | SPA 路由配置，所有 404 请求转向 index.html |
| `proxy_pass` | 将 /api 请求代理到后端 API |
| `expires` | 设置缓存时间 |
| `gzip on` | 启用 gzip 压缩 |

### 常见场景

#### 场景 1：前端应用在子路径
```nginx
location /app/ {
    alias /path/to/dist/;
    try_files $uri $uri/ /app/index.html;
}
```

#### 场景 2：多个前端应用
```nginx
server {
    listen 80;
    server_name app1.com;
    root /path/to/app1/dist;
    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name app2.com;
    root /path/to/app2/dist;
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### 场景 3：HTTPS 部署
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 其他配置...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 常用命令

```bash
# 测试配置文件
nginx -t

# 重新加载配置（不中断服务）
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 停止 Nginx
sudo systemctl stop nginx

# 查看 Nginx 进程
ps aux | grep nginx
```

---

## 故障排查

### 问题 1：访问 URL 时出现 404
**原因**: 没有配置 SPA 路由转向
**解决**: 确保配置了 `try_files $uri $uri/ /index.html;`

### 问题 2：API 请求跨域错误
**原因**: 代理配置错误或后端没有 CORS 配置
**解决**: 检查 `proxy_pass` 是否正确指向后端地址

### 问题 3：静态资源加载失败
**原因**: root 路径配置错误
**解决**: 确保 root 指向正确的 dist 目录路径

### 问题 4：Nginx 启动失败
**解决**: 
```bash
sudo nginx -t  # 查看错误信息
sudo tail -f /var/log/nginx/error.log  # 查看日志
```

---

## 性能优化建议

1. **启用 gzip 压缩**: 减少传输大小
2. **设置合理的缓存策略**: 
   - 无 hash 的文件（index.html）: `max-age=0`
   - 有 hash 的文件（assets）: `max-age=31536000`
3. **使用 HTTP/2**: 提高并发性能
4. **CDN 加速**: 在生产环境使用 CDN 分发静态资源

---

## Windows 本地开发快速测试

1. 下载 Nginx 到本地
2. 修改 conf/nginx.conf：
```nginx
server {
    listen 8080;
    server_name localhost;
    root C:/your/project/dist;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```
3. 在 nginx.exe 所在目录运行：
```bash
nginx.exe
```
4. 访问 http://localhost:8080

---

## 更多资源

- [Nginx 官方文档](http://nginx.org/en/docs/)
- [Nginx 配置参考](http://nginx.org/en/docs/http/ngx_http_core_module.html)
