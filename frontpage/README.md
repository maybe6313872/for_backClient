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
