#!/bin/bash

# 智检慧眼 - Linux服务器部署脚本
# 适用于 Ubuntu/CentOS/Debian

set -e

echo "========================================="
echo "  智检慧眼 - 车辆智能检测系统部署脚本"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo -e "${YELLOW}检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3，请先安装Python 3.9+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python版本: $PYTHON_VERSION${NC}"

# 创建虚拟环境
echo -e "\n${YELLOW}创建虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"

# 安装依赖
echo -e "\n${YELLOW}安装Python依赖...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 复制环境配置文件
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}创建环境配置文件...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ 已创建.env文件，请根据实际需求修改配置${NC}"
else
    echo -e "\n${YELLOW}✓ .env文件已存在${NC}"
fi

# 创建必要目录
echo -e "\n${YELLOW}创建必要目录...${NC}"
mkdir -p static/upload
mkdir -p data
mkdir -p logs
echo -e "${GREEN}✓ 目录创建完成${NC}"

# 初始化数据库
echo -e "\n${YELLOW}初始化数据库...${NC}"
python3 -c "from models.database import init_db; init_db(); print('数据库初始化成功')"
echo -e "${GREEN}✓ 数据库初始化完成${NC}"

# 创建systemd服务文件
echo -e "\n${YELLOW}创建systemd服务配置...${NC}"
SERVICE_FILE="/etc/systemd/system/car-detect.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=智检慧眼 - 车辆智能检测系统
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ systemd服务配置创建完成${NC}"

# 重载systemd
echo -e "\n${YELLOW}重载systemd配置...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable car-detect.service
echo -e "${GREEN}✓ 服务已启用${NC}"

# 启动服务
echo -e "\n${YELLOW}启动服务...${NC}"
sudo systemctl start car-detect.service

# 检查服务状态
sleep 3
if sudo systemctl is-active --quiet car-detect.service; then
    echo -e "${GREEN}✓ 服务启动成功！${NC}"
    echo -e "\n${GREEN}=========================================${NC}"
    echo -e "${GREEN}  部署完成！${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo -e "访问地址: http://YOUR_SERVER_IP:8000"
    echo -e "API文档: http://YOUR_SERVER_IP:8000/docs"
    echo -e "\n常用命令:"
    echo -e "  查看状态: sudo systemctl status car-detect"
    echo -e "  重启服务: sudo systemctl restart car-detect"
    echo -e "  查看日志: sudo journalctl -u car-detect -f"
    echo -e "  停止服务: sudo systemctl stop car-detect"
else
    echo -e "${RED}✗ 服务启动失败，请检查日志${NC}"
    echo -e "查看日志: sudo journalctl -u car-detect -n 50"
    exit 1
fi
