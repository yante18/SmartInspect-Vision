#!/bin/bash

# 项目打包脚本 - 生成可部署的压缩包

set -e

echo "========================================="
echo "  智检慧眼 - 项目打包脚本"
echo "========================================="

PROJECT_NAME="car_detect"
VERSION="1.0.0"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="${PROJECT_NAME}_v${VERSION}_${TIMESTAMP}"

# 清理旧的打包文件
if [ -d "build" ]; then
    echo "清理旧的构建文件..."
    rm -rf build
fi

mkdir -p build

echo "准备打包文件..."

# 复制项目文件（排除不必要的文件）
rsync -av --exclude='venv' \
         --exclude='__pycache__' \
         --exclude='*.pyc' \
         --exclude='.git' \
         --exclude='data/*.db' \
         --exclude='logs/*.log' \
         --exclude='static/upload/*' \
         --include='static/upload/.gitkeep' \
         . "build/${ARCHIVE_NAME}/"

echo "创建压缩包..."

# 创建tar.gz压缩包
cd build
tar -czf "${ARCHIVE_NAME}.tar.gz" "${ARCHIVE_NAME}/"

# 创建zip压缩包（Windows友好）
if command -v zip &> /dev/null; then
    zip -r "${ARCHIVE_NAME}.zip" "${ARCHIVE_NAME}/" > /dev/null
fi

cd ..

echo ""
echo "========================================="
echo "  打包完成！"
echo "========================================="
echo ""
echo "生成的文件："
ls -lh build/${ARCHIVE_NAME}.*
echo ""
echo "部署说明："
echo "1. 将压缩包上传到服务器"
echo "2. 解压: tar -xzf ${ARCHIVE_NAME}.tar.gz"
echo "3. 进入目录: cd ${ARCHIVE_NAME}"
echo "4. 执行部署: sudo ./deploy.sh"
echo ""
