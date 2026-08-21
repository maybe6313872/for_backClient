# Swagger 文档问题排查指南

## 已完成的优化

1. ✅ 为所有路由添加了 `tags` 和 `summary` 描述
2. ✅ 为 FastAPI 应用添加了标题、描述和版本信息
3. ✅ 明确配置了文档路径（`/docs`, `/redoc`, `/openapi.json`）

## 验证 Swagger 文档是否正常

运行测试脚本：
```bash
python test_swagger.py
```

如果看到所有路由列表，说明文档生成正常。

## 启动服务并访问 Swagger

1. **启动服务**：
   ```bash
   uvicorn main:app --reload
   ```
   或者使用：
   ```bash
   python -m uvicorn main:app --reload
   ```

2. **访问 Swagger UI**：
   - 打开浏览器访问：http://localhost:8000/docs
   - 或者访问 ReDoc：http://localhost:8000/redoc
   - 或者查看 OpenAPI JSON：http://localhost:8000/openapi.json

## 常见问题排查

### 问题1: 访问 /docs 显示空白或404

**解决方案**：
- 检查服务是否正常启动（查看终端输出）
- 确认访问的URL正确：http://localhost:8000/docs
- 检查是否有错误日志
- 尝试清除浏览器缓存或使用无痕模式

### 问题2: 路由没有显示在 Swagger 中

**可能原因**：
- 路由导入失败（检查启动日志中的错误）
- 依赖项加载失败（如数据库连接、邮件配置等）

**解决方案**：
```bash
# 检查应用是否能正常加载
python -c "from main import app; print('OK')"

# 检查路由数量
python -c "from main import app; print(f'Routes: {len(app.routes)}')"
```

### 问题3: 依赖项错误导致路由无法加载

如果某些依赖项（如数据库连接）在启动时失败，可能导致路由无法注册。

**解决方案**：
- 检查 `dependencies.py` 中的依赖项配置
- 确保数据库连接配置正确
- 确保邮件服务配置正确
- 查看启动日志中的错误信息

### 问题4: 端口被占用

**解决方案**：
```bash
# Windows 检查端口占用
netstat -ano | findstr :8000

# 使用其他端口启动
uvicorn main:app --reload --port 8001
```

## 当前配置的路由

根据测试脚本输出，以下路由应该显示在 Swagger 中：

- `GET /` - 根路径
- `GET /auth/code` - 获取邮箱验证码
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /hello/{name}` - 问候接口
- `GET /mail/test` - 邮件测试
- `POST /name/` - 生成名字

## 验证步骤

1. ✅ 运行 `python test_swagger.py` 确认文档生成正常
2. ✅ 启动服务：`uvicorn main:app --reload`
3. ✅ 访问 http://localhost:8000/docs
4. ✅ 检查是否能看到所有7个路由
5. ✅ 检查每个路由的详细信息是否正确显示

## 如果问题仍然存在

请提供以下信息：
1. 服务启动时的完整日志
2. 访问 `/docs` 时的浏览器控制台错误（F12查看）
3. 访问 `/openapi.json` 的响应内容
4. 运行 `python test_swagger.py` 的输出
