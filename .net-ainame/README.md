# 知了 AI 起名 — .NET 后端

本目录为使用 **ASP.NET Core** 重写原 Python（`zhiliao-ainame`）核心 API 的工程根目录。

- 解决方案：`Zhiliao.Ainame.sln`
- Web 项目：`Zhiliao.Ainame.Api`

功能已从 `zhiliao-ainame`（FastAPI）**整库迁移**：认证、起名、文章与 Excel、省市区（Redis）、校园、订单等。

## 快速启动（最短路径）

1. 安装 **.NET 9 SDK**，终端执行 `dotnet --version` 应显示 **9.x**。
2. 启动 **MySQL**，准备好数据库 **`zhiliao_ainame`**（表可与 Python 项目 `zhiliao-ainame` 共用）。
3. 编辑 **`Zhiliao.Ainame.Api/appsettings.Development.json`**，把 `ConnectionStrings:DefaultConnection` 里的密码改成你的 MySQL 密码。
4. 在 **本目录**（含 `Zhiliao.Ainame.sln`）打开终端，**逐行**执行（PowerShell 5 不要用 `&&`）：

   ```powershell
   dotnet restore
   dotnet build
   dotnet run --project Zhiliao.Ainame.Api
   ```

5. 浏览器打开 **http://localhost:5027/docs**（Swagger）。根路径：**http://localhost:5027/**。  
   **省市区接口**依赖 **Redis**（默认 `127.0.0.1:6379`）；不测 `/region/*` 时可暂不装 Redis。

**逐步说明、VS 启动、`dotnet watch`、User Secrets、改端口与排错** 见 **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** 文首 **《启动项目（具体操作）》** 与 **第 13 节**。

---

**学习向完整文档**（技术栈、与 FastAPI 对照、目录结构、请求流水线、日常开发循环、调试、EF、JWT 等）见 **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**。
