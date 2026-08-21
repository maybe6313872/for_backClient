@echo off
REM Docker 镜像构建脚本 (Windows)

echo ==========================================
echo 开始构建 Docker 镜像
echo ==========================================

REM 检查 Docker 是否安装
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Docker，请先安装 Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM 镜像名称和标签
set IMAGE_NAME=zhiliao-ainame
set IMAGE_TAG=%1
if "%IMAGE_TAG%"=="" set IMAGE_TAG=latest

echo 镜像名称: %IMAGE_NAME%:%IMAGE_TAG%
echo.

REM 构建镜像
echo 正在构建镜像...
docker build -t %IMAGE_NAME%:%IMAGE_TAG% .

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo 镜像构建成功！
    echo ==========================================
    echo.
    echo 镜像信息:
    docker images | findstr %IMAGE_NAME%
    echo.
    echo 运行容器命令:
    echo   docker run -d -p 8000:8000 --name zhiliao-ainame %IMAGE_NAME%:%IMAGE_TAG%
    echo.
    echo 或使用 docker-compose:
    echo   docker-compose up -d
) else (
    echo.
    echo ==========================================
    echo 镜像构建失败
    echo ==========================================
    exit /b 1
)
