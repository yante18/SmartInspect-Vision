#!/bin/bash

# 智检慧眼 - Docker一键部署脚本（本地执行）
# 通过SSH自动部署到Ubuntu服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  智检慧眼 - Docker自动化部署脚本${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# ==================== 配置区域 ====================
# 请修改以下配置为您的服务器信息
SERVER_USER="root"              # SSH用户名
SERVER_HOST="yan"    # 服务器IP地址（使用SSH别名）
SERVER_PORT="22"                # SSH端口
DEPLOY_PATH="/opt/car-detect"   # 服务器部署路径
DOCKER_COMPOSE_VERSION="v2.20.0" # Docker Compose版本

# ==================== 函数定义 ====================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_step "检查本地依赖..."
    
    if ! command -v ssh &> /dev/null; then
        log_error "未找到ssh命令，请先安装OpenSSH客户端"
        exit 1
    fi
    
    if ! command -v scp &> /dev/null; then
        log_error "未找到scp命令，请先安装OpenSSH客户端"
        exit 1
    fi
    
    log_info "✓ SSH和SCP命令可用"
}

# 测试SSH连接
test_ssh_connection() {
    log_step "测试SSH连接..."
    
    if ssh -p "$SERVER_PORT" -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_HOST" "echo 'Connection successful'" &> /dev/null; then
        log_info "✓ SSH连接成功"
        return 0
    else
        log_error "✗ SSH连接失败，请检查："
        echo "  1. 服务器IP地址是否正确: $SERVER_HOST"
        echo "  2. SSH端口是否正确: $SERVER_PORT"
        echo "  3. 用户名是否正确: $SERVER_USER"
        echo "  4. SSH密钥是否已配置"
        echo ""
        echo "提示：首次连接可能需要手动确认指纹"
        echo "运行以下命令测试连接："
        echo "  ssh -p $SERVER_PORT $SERVER_USER@$SERVER_HOST"
        exit 1
    fi
}

# 上传项目文件
upload_project() {
    log_step "打包项目文件..."
    
    # 创建临时打包目录
    TEMP_DIR=$(mktemp -d)
    PROJECT_NAME="car_detect_deploy"
    
    # 复制必要文件（排除不必要的文件）
    rsync -av --exclude='venv' \
             --exclude='__pycache__' \
             --exclude='*.pyc' \
             --exclude='.git' \
             --exclude='data/*.db' \
             --exclude='logs/*.log' \
             --exclude='static/upload/*' \
             --include='static/upload/.gitkeep' \
             --include='.env.example' \
             . "$TEMP_DIR/$PROJECT_NAME/" 2>/dev/null || cp -r . "$TEMP_DIR/$PROJECT_NAME/"
    
    log_info "✓ 项目文件打包完成"
    
    log_step "上传到服务器 ($SERVER_USER@$SERVER_HOST:$DEPLOY_PATH)..."
    
    # 在服务器上创建部署目录
    ssh -p "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST" "mkdir -p $DEPLOY_PATH"
    
    # 上传文件
    scp -p "$SERVER_PORT" -r "$TEMP_DIR/$PROJECT_NAME/"* "$SERVER_USER@$SERVER_HOST:$DEPLOY_PATH/"
    
    log_info "✓ 文件上传完成"
    
    # 清理临时目录
    rm -rf "$TEMP_DIR"
}

# 在服务器上执行部署
deploy_on_server() {
    log_step "在服务器上执行部署..."
    
    ssh -p "$SERVER_PORT" "$SERVER_USER@$SERVER_HOST" << 'ENDSSH'
#!/bin/bash
set -e

echo "========================================="
echo "  开始在服务器上部署..."
echo "========================================="

cd /opt/car-detect

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "[错误] Docker未安装，请先安装Docker"
    exit 1
fi

echo "[1/6] Docker版本:"
docker --version

# 检查Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "[警告] Docker Compose V2未找到，尝试安装..."
    
    # 下载Docker Compose
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    
    echo "[✓] Docker Compose安装完成"
else
    echo "[✓] Docker Compose已安装"
    docker compose version
fi

# 创建环境配置文件
if [ ! -f .env ]; then
    echo "[2/6] 创建环境配置文件..."
    cp .env.example .env
    echo "[✓] .env文件已创建"
else
    echo "[2/6] .env文件已存在"
fi

# 创建必要目录
echo "[3/6] 创建必要目录..."
mkdir -p static/upload data logs
chmod -R 755 static/upload data logs
echo "[✓] 目录创建完成"

# 停止旧容器（如果存在）
echo "[4/6] 停止旧容器..."
docker compose down 2>/dev/null || true
echo "[✓] 旧容器已停止"

# 构建并启动新容器
echo "[5/6] 构建并启动容器..."
docker compose up -d --build
echo "[✓] 容器启动成功"

# 等待服务就绪
echo "[6/6] 等待服务就绪..."
sleep 5

# 检查容器状态
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "========================================="
    echo "  ✓ 部署成功！"
    echo "========================================="
    echo ""
    echo "容器状态:"
    docker compose ps
    echo ""
    echo "访问地址: http://YOUR_SERVER_IP:8000"
    echo "API文档: http://YOUR_SERVER_IP:8000/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker compose logs -f"
    echo "  重启服务: docker compose restart"
    echo "  停止服务: docker compose down"
    echo "  更新部署: ./deploy.sh (重新运行此脚本)"
else
    echo ""
    echo "[错误] 容器启动失败，请检查日志:"
    docker compose logs
    exit 1
fi
ENDSSH
    
    log_info "✓ 服务器部署完成"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  🎉 部署完成！${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo -e "📍 服务器: ${YELLOW}$SERVER_USER@$SERVER_HOST${NC}"
    echo -e "📁 部署路径: ${YELLOW}$DEPLOY_PATH${NC}"
    echo -e "🌐 访问地址: ${YELLOW}http://$SERVER_HOST:8000${NC}"
    echo -e "📖 API文档: ${YELLOW}http://$SERVER_HOST:8000/docs${NC}"
    echo ""
    echo -e "${BLUE}管理命令:${NC}"
    echo "  查看日志:     ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker compose logs -f'"
    echo "  重启服务:     ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker compose restart'"
    echo "  停止服务:     ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker compose down'"
    echo "  查看状态:     ssh $SERVER_USER@$SERVER_HOST 'cd $DEPLOY_PATH && docker compose ps'"
    echo "  进入容器:     ssh $SERVER_USER@$SERVER_HOST 'docker exec -it car-detect-app bash'"
    echo ""
    echo -e "${YELLOW}提示: 将本脚本中的SERVER_HOST修改为您的实际服务器IP${NC}"
    echo ""
}

# ==================== 主流程 ====================

main() {
    # 检查配置
    if [ "$SERVER_HOST" = "your-server-ip" ]; then
        log_error "请先修改脚本中的服务器配置！"
        echo ""
        echo "需要修改的配置项："
        echo "  SERVER_USER=\"$SERVER_USER\"     # SSH用户名"
        echo "  SERVER_HOST=\"$SERVER_HOST\"  # 服务器IP"
        echo "  SERVER_PORT=\"$SERVER_PORT\"          # SSH端口"
        echo ""
        exit 1
    fi
    
    check_dependencies
    test_ssh_connection
    upload_project
    deploy_on_server
    show_deployment_info
}

# 执行主流程
main
