#!/bin/bash
# Docker 镜像构建脚本

set -e

echo "=========================================="
echo "开始构建 Docker 镜像"
echo "=========================================="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: 未找到 Docker，请先安装 Docker"
    echo "Windows: 下载并安装 Docker Desktop"
    echo "Linux: sudo apt-get install docker.io"
    exit 1
fi

# 镜像名称和标签
IMAGE_NAME="zhiliao-ainame"
IMAGE_TAG="${1:-latest}"

echo "镜像名称: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# 构建镜像
echo "正在构建镜像..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 镜像构建成功！"
    echo "=========================================="
    echo ""
    echo "镜像信息:"
    docker images | grep ${IMAGE_NAME}
    echo ""
    echo "运行容器命令:"
    echo "  docker run -d -p 8000:8000 --name zhiliao-ainame ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    echo "或使用 docker-compose:"
    echo "  docker-compose up -d"
else
    echo ""
    echo "=========================================="
    echo "❌ 镜像构建失败"
    echo "=========================================="
    exit 1
fi
