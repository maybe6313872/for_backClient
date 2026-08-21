# nodejs-ainame

**知了AI起名 API** 的 Node.js 实现版本，以 [zhiliao-ainame](https://github.com/...)（FastAPI）项目为蓝本，使用主流、稳定的技术栈重新开发。

## 技术栈

| 类别     | 技术           | 说明                    |
|----------|----------------|-------------------------|
| 运行时   | Node.js 18+    | LTS 长期支持            |
| 语言     | TypeScript 5.x | 类型安全与可维护性      |
| Web 框架 | Express 4.x    | 稳定、生态成熟          |
| 数据库   | MySQL + Prisma | ORM，类型安全、迁移友好 |
| 缓存     | Redis (ioredis)| 省市区等数据            |
| 认证     | JWT (jsonwebtoken) + Argon2 | 登录与密码哈希   |
| 邮件     | Nodemailer     | SMTP 发送验证码等       |
| 文件上传 | Multer         | 文章缩略图、Excel       |
| Excel    | xlsx (SheetJS)  | 导出/导入文章           |
| 校验     | Zod            | 请求体与查询参数校验    |

## 项目结构

```
nodejs-ainame/
├── prisma/
│   └── schema.prisma      # 数据模型（与 FastAPI 版表结构对齐）
├── src/
│   ├── config/            # 配置（环境变量）
│   ├── lib/               # 基础设施：Prisma、Redis、邮件
│   ├── middleware/        # 认证、上传
│   ├── routes/            # 路由
│   │   ├── auth.ts        # 认证：验证码、注册、登录
│   │   ├── name.ts        # AI 起名
│   │   ├── region.ts      # 省市区（Redis）
│   │   ├── school.ts      # 学校 CRUD
│   │   ├── admin/         # 管理端：文章、Excel
│   │   └── order/         # 公司、产品、订单
│   └── index.ts           # 应用入口
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

## 环境要求

- Node.js >= 18
- MySQL 5.7+ / 8.0
- Redis（可选，用于省市区接口）

## 快速开始

### 1. 安装依赖

```bash
cd nodejs-ainame
npm install
```

### 2. 环境变量

复制示例并按需修改：

```bash
cp .env.example .env
```

必填项示例：

- `DATABASE_URL`：MySQL 连接串，例如  
  `mysql://root:root@127.0.0.1:3306/zhiliao_ainame?charset=utf8mb4`
- `JWT_SECRET_KEY`：生产环境务必使用强随机密钥
- 邮件相关：`MAIL_USERNAME`、`MAIL_PASSWORD`、`MAIL_FROM` 等（发验证码、测试邮件）

### 3. 数据库迁移

```bash
npm run prisma:generate
npm run prisma:push
```

若需使用迁移文件：

```bash
npm run prisma:migrate
```

### 4. 启动

开发（热重载）：

```bash
npm run dev
```

生产：

```bash
npm run build
npm start
```

默认端口：**3000**，可通过环境变量 `PORT` 修改。

## 生产部署（打完包后部署到服务器）

### 一、服务器环境准备

1. **安装 Node.js 18+**
   ```bash
   # 以 Ubuntu 为例
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install -y nodejs
   node -v   # 确认 >= 18
   ```

2. **安装并启动 MySQL、Redis**（若尚未安装）
   - MySQL：创建好数据库（如 `zhiliao_ainame`），记下连接信息。
   - Redis：省市区接口依赖，可选但建议开启。

### 二、本地打包

在开发机项目根目录执行：

```bash
cd nodejs-ainame
npm install
npm run build
```

得到编译后的 `dist/` 目录（以及已有的 `prisma/`、`package.json` 等）。

### 三、上传到服务器

需要上传的内容（**不要**上传 `node_modules`、`.env`、`src/` 源码可选不传）：

| 必须上传 | 说明 |
|----------|------|
| `dist/` | 编译后的 JS 入口与路由 |
| `prisma/` | 含 `schema.prisma`，用于生成 Prisma Client 和迁移 |
| `package.json` | 依赖与脚本 |
| `package-lock.json` | 有则上传，保证依赖版本一致 |

可选：`tsconfig.json` 仅开发用，部署可不传。  
**不要**把本地 `.env` 直接传到生产；在服务器上新建并填写生产配置。

示例（在服务器上创建目录并上传，或用 SCP/rsync/Git 等）：

```bash
# 在服务器上
mkdir -p /opt/ainame-api
cd /opt/ainame-api
# 然后用 scp / rsync / git clone 等方式把 dist、prisma、package.json、package-lock.json 拷到此处
```

### 四、服务器上安装依赖并生成 Prisma

```bash
cd /opt/ainame-api
npm install --production
npx prisma generate
```

`--production` 只装运行时依赖，不装 devDependencies。  
`prisma generate` 会根据 `prisma/schema.prisma` 生成 Prisma Client（写入 `node_modules`），运行时会用到。

### 五、配置环境变量

在项目根目录创建 `.env`（不要提交到 Git）：

```bash
cp .env.example .env
vim .env   # 或 nano .env
```

生产环境至少修改：

- `DATABASE_URL`：指向服务器 MySQL（库已创建好）
- `JWT_SECRET_KEY`：使用强随机字符串
- `REDIS_URL`：服务器 Redis 地址（若用省市区接口）
- 邮件相关：`MAIL_*` 按实际 SMTP 填写
- 可选：`PORT=3000`，或由进程管理器指定

### 六、数据库迁移（首次或升级后）

```bash
# 仅同步 schema，不生成迁移文件
npx prisma db push

# 或使用迁移（需先有迁移文件）
# npx prisma migrate deploy
```

确认数据库表与 Prisma schema 一致后再启动应用。

### 七、启动应用

**方式 1：直接前台运行（仅用于试跑）**

```bash
npm start
# 或
node dist/index.js
```

**方式 2：用 PM2 守护（推荐）**

```bash
npm install -g pm2
pm2 start dist/index.js --name ainame-api
pm2 save
pm2 startup   # 按提示设置开机自启
pm2 logs ainame-api
```

**方式 3：systemd**

创建 `/etc/systemd/system/ainame-api.service`，例如：

```ini
[Unit]
Description=Ainame API
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ainame-api
ExecStart=/usr/bin/node dist/index.js
Restart=on-failure
Environment=NODE_ENV=production
EnvironmentFile=/opt/ainame-api/.env

[Install]
WantedBy=multi-user.target
```

然后：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ainame-api
sudo systemctl start ainame-api
sudo systemctl status ainame-api
```

### 八、反向代理与端口

应用默认监听 3000。生产建议用 Nginx 做反向代理并配 HTTPS，例如：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 部署步骤小结

| 步骤 | 命令/操作 |
|------|-----------|
| 1. 服务器装 Node 18+、MySQL、Redis | 见上文 |
| 2. 本地打包 | `npm install` → `npm run build` |
| 3. 上传 | `dist/`、`prisma/`、`package.json`（及 lock） |
| 4. 服务器安装 | `npm install --production` → `npx prisma generate` |
| 5. 配置 | 新建 `.env` 并填写生产配置 |
| 6. 数据库 | `npx prisma db push` 或 `migrate deploy` |
| 7. 启动 | `npm start` 或 PM2 或 systemd |
| 8. 对外访问 | Nginx 反代 3000，可选 HTTPS |

## API 说明

与 FastAPI 版保持一致的路径与语义，便于前后端切换或并行使用。

### 通用

| 方法 | 路径            | 说明         |
|------|-----------------|--------------|
| GET  | /               | 健康检查     |
| GET  | /hello/:name    | 问候         |
| GET  | /mail/test      | 邮件测试（query: email） |

### 认证 `/auth`

| 方法 | 路径        | 说明                 |
|------|-------------|----------------------|
| GET  | /auth/code  | 发送邮箱验证码（query: email） |
| POST | /auth/register | 注册（body: email, username, password, confirm_password, code） |
| POST | /auth/login | 登录（body: email, password），返回 user + token |

### 起名 `/name`

| 方法 | 路径   | 说明 |
|------|--------|------|
| POST | /name  | 起名（body: surname, gender, length, other?, exclude?），当前返回示例数据，可后续接入 AI |

### 管理端 `/admin`

| 方法 | 路径               | 说明 |
|------|--------------------|------|
| POST | /admin/insertArt    | 新增文章（multipart: username, sex, artcontent, file） |
| POST | /admin/delArt      | 批量删除（body: idArr） |
| POST | /admin/changeArt   | 修改文章（body: id, sex） |
| POST | /admin/queryArt    | 查询文章（需 JWT）（body: page, size, sex） |
| POST | /admin/queryArtOut  | 查询文章（标准包装，无需 JWT） |
| POST | /admin/queryArtExcel | 导出文章为 Excel（body: page, size, sex） |
| POST | /admin/insertArtByExcel | 从 Excel 批量导入（multipart: file, username?） |

### 省市区 `/region`（依赖 Redis）

| 方法 | 路径              | 说明 |
|------|-------------------|------|
| GET  | /region/provinces  | 省份列表 |
| GET  | /region/cities     | 城市列表（query: province_code） |
| GET  | /region/districts  | 区县列表（query: city_code） |
| POST | /region/init       | 初始化省市区数据到 Redis |

### 学校 `/school`

| 方法 | 路径              | 说明 |
|------|-------------------|------|
| POST | /school           | 创建（body: name, address） |
| GET  | /school           | 列表 |
| GET  | /school/:school_id | 详情 |
| PUT  | /school/:school_id | 更新 |
| DELETE | /school/:school_id | 删除 |

### 班主任 `/teacher`

| 方法 | 路径                | 说明 |
|------|---------------------|------|
| POST | /teacher            | 创建（body: name, sex, age, school_id） |
| GET  | /teacher            | 列表（query: school_id 可选） |
| GET  | /teacher/:teacher_id | 详情 |
| PUT  | /teacher/:teacher_id | 更新 |
| DELETE | /teacher/:teacher_id | 删除 |

### 学生 `/student`

| 方法 | 路径                | 说明 |
|------|---------------------|------|
| POST | /student            | 创建（body: name, sex, age, teacher_id） |
| GET  | /student            | 列表含选课与分数（query: teacher_id 可选） |
| GET  | /student/:student_id | 详情含选课与分数 |
| PUT  | /student/:student_id | 更新 |
| DELETE | /student/:student_id | 删除 |

### 课程 `/course`

| 方法 | 路径              | 说明 |
|------|-------------------|------|
| POST | /course           | 创建（body: name, credit） |
| GET  | /course           | 列表 |
| GET  | /course/:course_id | 详情 |
| PUT  | /course/:course_id | 更新 |
| DELETE | /course/:course_id | 删除 |

### 学生选课 `/student-course`

| 方法 | 路径                                    | 说明 |
|------|-----------------------------------------|------|
| POST | /student-course                         | 批量选课（body: student_id, course_ids, scores?），先清空再添加 |
| POST | /student-course/single                  | 单条选课（body: student_id, course_id, score?） |
| GET  | /student-course                         | 列表（query: student_id / course_id 可选） |
| GET  | /student-course/course/:course_id/students | 某课程下的学生列表（含分数） |
| GET  | /student-course/:id                     | 单条关联详情 |
| PUT  | /student-course/:id                     | 更新（主要更新 score） |
| DELETE | /student-course/:id                     | 删除（退课） |

### 公司 `/company`

| 方法 | 路径                | 说明 |
|------|---------------------|------|
| POST | /company/create     | 创建 |
| GET  | /company/query      | 列表 |
| PUT  | /company/update     | 更新（body: id, name, address） |
| DELETE | /company/delete   | 删除（query: company_id） |

### 产品 `/product`

| 方法 | 路径                | 说明 |
|------|---------------------|------|
| POST | /product/create     | 创建 |
| GET  | /product/query      | 列表 |
| PUT  | /product/update     | 更新 |
| DELETE | /product/delete   | 删除（query: prduct_id 或 product_id） |

### 订单 `/order`

| 方法 | 路径            | 说明 |
|------|-----------------|------|
| POST | /order/create   | 创建（body: order_number, company_id, product_list） |
| PUT  | /order/update   | 更新（body: id, order_number, company_id, product_list） |
| GET  | /order/query    | 列表 |
| DELETE | /order/delete   | 删除（query: id） |

## 认证方式

登录接口返回的 `token` 需在请求头中携带：

```
Authorization: Bearer <token>
```

需要登录的接口：`POST /admin/queryArt` 等，未带有效 token 将返回 403。

## 与 FastAPI 版的对应关系

- 表结构通过 Prisma schema 与 FastAPI 使用的 MySQL 表对齐（表名、字段名、关系）。
- 接口路径、请求方法、主要请求/响应格式与 FastAPI 版一致，便于复用前端或迁移。
- 省市区数据与 Redis key 设计保持一致，可与原项目共用同一 Redis。

## 开发与调试

- 使用 `npm run dev` 时，修改代码会自动重启。
- 生产环境建议设置 `NODE_ENV=production`，并配置反向代理（如 Nginx）与 HTTPS。

## 许可证

MIT
