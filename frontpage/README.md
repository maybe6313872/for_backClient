# 后台管理系统仪表盘

基于Vue 3实现的后台管理系统仪表盘界面，完全还原设计图中的所有元素和样式。

## 功能特性

- ✅ 左侧导航栏（深蓝色主题）
- ✅ 顶部头部栏（搜索、通知、用户信息）
- ✅ 仪表盘数据卡片（总销售额、新增用户、订单数量、访问量）
- ✅ 销售趋势图表（柱状图）
- ✅ 用户增长图表（柱状图）
- ✅ 最新订单列表区域

## 技术栈

- Vue 3
- Vue Router
- ECharts（图表库）
- Vite（构建工具）

## 安装和运行

1. 安装依赖：
```bash
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 项目结构

```
├── src/
│   ├── components/        # 组件目录
│   │   ├── Sidebar.vue   # 左侧导航栏
│   │   ├── Header.vue    # 顶部头部栏
│   │   ├── StatCard.vue  # 数据统计卡片
│   │   └── ChartCard.vue # 图表卡片
│   ├── views/            # 视图目录
│   │   └── Dashboard.vue # 仪表盘主页面
│   ├── router/           # 路由配置
│   ├── App.vue           # 根组件
│   ├── main.js           # 入口文件
│   └── style.css         # 全局样式
├── index.html
├── package.json
└── vite.config.js
```

## 浏览器支持

现代浏览器（Chrome、Firefox、Safari、Edge等）

## 在手机或 Android 模拟器中访问开发服务器

Vite 开发服务器监听所有网卡（`0.0.0.0:3000`），因此除本机 `http://localhost:3000` 外，也可从同一局域网中的设备访问开发电脑的局域网 IP，例如 `http://192.168.1.20:3000`。启动方式仍为：

```bash
npm run dev
```

- Android Studio 模拟器访问开发电脑请使用 `http://10.0.2.2:3000`；模拟器里的 `localhost` 指模拟器本身，不是电脑。
- 真机与开发电脑连接同一 Wi-Fi 后，使用开发电脑的局域网 IPv4 地址，例如 `http://192.168.1.20:3000`。
- Windows 防火墙需允许 Node.js/Vite 接收 TCP 3000 端口的入站连接。
- 前端的 `/api` 请求仍由 Vite 代理到开发电脑上的 `http://localhost:8000`，无需在浏览器端改成后端 IP。
