#!/bin/bash

# 智检慧眼 - Docker容器管理脚本（在服务器上执行）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DEPLOY_PATH="/opt/car-detect"

show_menu() {
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}  智检慧眼 - Docker容器管理${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
    echo "1. 查看容器状态"
    echo "2. 查看实时日志"
    echo "3. 重启服务"
    echo "4. 停止服务"
    echo "5. 启动服务"
    echo "6. 更新部署（重新构建）"
    echo "7. 进入容器"
    echo "8. 备份数据"
    echo "9. 清理无用资源"
    echo "0. 退出"
    echo ""
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[错误] Docker未安装${NC}"
        exit 1
    fi
    
    if ! command -v docker compose &> /dev/null; then
        echo -e "${RED}[错误] Docker Compose未安装${NC}"
        exit 1
    fi
}

status() {
    echo -e "${GREEN}[信息] 容器状态:${NC}"
    cd $DEPLOY_PATH
    docker compose ps
}

logs() {
    echo -e "${GREEN}[信息] 实时日志（Ctrl+C退出）:${NC}"
    cd $DEPLOY_PATH
    docker compose logs -f
}

restart() {
    echo -e "${YELLOW}[操作] 重启服务...${NC}"
    cd $DEPLOY_PATH
    docker compose restart
    echo -e "${GREEN}[成功] 服务已重启${NC}"
}

stop() {
    echo -e "${YELLOW}[操作] 停止服务...${NC}"
    cd $DEPLOY_PATH
    docker compose down
    echo -e "${GREEN}[成功] 服务已停止${NC}"
}

start() {
    echo -e "${YELLOW}[操作] 启动服务...${NC}"
    cd $DEPLOY_PATH
    docker compose up -d
    echo -e "${GREEN}[成功] 服务已启动${NC}"
}

update() {
    echo -e "${YELLOW}[操作] 更新部署...${NC}"
    cd $DEPLOY_PATH
    
    echo "[1/2] 拉取最新代码..."
    # 如果有git，可以取消注释
    # git pull
    
    echo "[2/2] 重启容器（代码通过卷挂载，自动生效）..."
    docker compose restart
    
    echo -e "${GREEN}[成功] 更新完成${NC}"
}

exec_container() {
    echo -e "${YELLOW}[操作] 进入容器...${NC}"
    docker exec -it car-detect-app bash
}

backup() {
    echo -e "${YELLOW}[操作] 备份数据...${NC}"
    
    BACKUP_DIR="/opt/car-detect-backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    cd $DEPLOY_PATH
    
    # 备份数据库
    if [ -f data/sensor.db ]; then
        cp data/sensor.db $BACKUP_DIR/
        echo "✓ 数据库已备份"
    fi
    
    # 备份上传文件
    if [ -d static/upload ]; then
        tar -czf $BACKUP_DIR/uploads.tar.gz static/upload/
        echo "✓ 上传文件已备份"
    fi
    
    # 备份配置文件
    if [ -f .env ]; then
        cp .env $BACKUP_DIR/
        echo "✓ 配置文件已备份"
    fi
    
    echo -e "${GREEN}[成功] 备份完成: $BACKUP_DIR${NC}"
}

prune() {
    echo -e "${YELLOW}[操作] 清理无用Docker资源...${NC}"
    docker system prune -f
    echo -e "${GREEN}[成功] 清理完成${NC}"
}

# 主程序
check_docker

while true; do
    show_menu
    read -p "请选择操作 (0-9): " choice
    
    case $choice in
        1) status ;;
        2) logs ;;
        3) restart ;;
        4) stop ;;
        5) start ;;
        6) update ;;
        7) exec_container ;;
        8) backup ;;
        9) prune ;;
        0) echo "退出"; exit 0 ;;
        *) echo -e "${RED}无效选择${NC}" ;;
    esac
    
    echo ""
    read -p "按回车键继续..."
done
