# 🐳 Docker部署指南

> 使用Docker快速部署智检慧眼系统到Ubuntu服务器

---

## 📋 前置要求

### 服务器环境
- ✅ Ubuntu 20.04 / 22.04 LTS
- ✅ 已安装 Docker（20.10+）
- ✅ 已安装 Docker Compose V2
- ✅ SSH访问权限
- ✅ 至少 1GB RAM，推荐 2GB+
- ✅ 至少 10GB 磁盘空间

### 本地环境
- ✅ SSH客户端
- ✅ SCP命令（用于文件传输）
- ✅ rsync命令（可选，用于增量同步）

---

## 🚀 快速部署（3步完成）

### 方式一：自动化脚本部署（推荐）

#### 步骤1：配置服务器信息

编辑 `docker-deploy.sh` 文件，修改以下配置：

```bash
SERVER_USER="root"              # 您的SSH用户名
SERVER_HOST="your-server-ip"    # 您的服务器IP地址
SERVER_PORT="22"                # SSH端口（默认22）
DEPLOY_PATH="/opt/car-detect"   # 服务器部署路径
```

#### 步骤2：赋予执行权限并运行

```bash
# 在本地项目目录执行
chmod +x docker-deploy.sh
./docker-deploy.sh
```

#### 步骤3：等待部署完成

脚本会自动：
- ✅ 测试SSH连接
- ✅ 上传项目文件
- ✅ 在服务器上构建Docker镜像
- ✅ 启动容器
- ✅ 验证服务状态

---

### 方式二：手动部署

#### 步骤1：上传项目到服务器

```bash
# 方法A：使用SCP
scp -r car_detect root@your-server-ip:/opt/

# 方法B：使用rsync（推荐，支持断点续传）
rsync -avz car_detect/ root@your-server-ip:/opt/car-detect/
```

#### 步骤2：SSH登录服务器

```bash
ssh root@your-server-ip
cd /opt/car-detect
```

#### 步骤3：配置环境变量

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件（可选）
nano .env
```

#### 步骤4：启动服务

```bash
# 使用Docker Compose启动
docker compose up -d --build

# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f
```

---

## 📝 配置说明

### 环境变量 (.env)

```env
# 应用配置
APP_PORT=8000                    # 映射到宿主机的端口
PROJECT_NAME=智检慧眼
API_PREFIX=/api/v1

# 文件上传配置
MAX_FILE_SIZE=10485760           # 10MB

# 日志级别
LOG_LEVEL=INFO                   # DEBUG/INFO/WARNING/ERROR
```

### Docker Compose配置

主要配置项在 `docker-compose.yml` 中：

```yaml
services:
  app:
    ports:
      - "8000:8000"              # 宿主机端口:容器端口
    
    volumes:
      - ./static/upload:/app/static/upload  # 上传文件持久化
      - ./data:/app/data                     # 数据库持久化
      - ./logs:/app/logs                     # 日志持久化
    
    deploy:
      resources:
        limits:
          memory: 2G              # 内存限制
          cpus: '2.0'             # CPU限制
```

---

## 🔧 常用管理命令

### 容器管理

```bash
# 进入项目目录
cd /opt/car-detect

# 查看容器状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 启动服务
docker compose up -d

# 更新部署（代码修改后）
docker compose up -d --build

# 进入容器内部
docker exec -it car-detect-app bash

# 查看容器资源使用
docker stats car-detect-app
```

### 使用管理脚本（推荐）

```bash
# 上传管理脚本到服务器
scp docker-manage.sh root@your-server-ip:/opt/car-detect/

# SSH登录服务器
ssh root@your-server-ip
cd /opt/car-detect

# 赋予执行权限并运行
chmod +x docker-manage.sh
./docker-manage.sh
```

管理脚本提供交互式菜单：
- 查看容器状态
- 查看实时日志
- 重启/停止/启动服务
- 更新部署
- 进入容器
- 备份数据
- 清理资源

---

## 🌐 配置域名和HTTPS

### 方式一：直接访问IP

```
http://YOUR_SERVER_IP:8000
```

### 方式二：使用Nginx反向代理

#### 1. 在服务器上安装Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

#### 2. 配置Nginx

```bash
# 复制配置文件
sudo cp docker-nginx.conf /etc/nginx/sites-available/car-detect

# 编辑配置文件，修改域名
sudo nano /etc/nginx/sites-available/car-detect
# 将 your-domain.com 改为您的实际域名

# 创建软链接
sudo ln -s /etc/nginx/sites-available/car-detect /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

#### 3. 配置HTTPS（Let's Encrypt）

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## 📊 监控和维护

### 查看日志

```bash
# 实时日志
docker compose logs -f

# 最近100行
docker compose logs --tail=100

# 仅错误日志
docker compose logs | grep ERROR

# 导出日志到文件
docker compose logs > logs/export_$(date +%Y%m%d).log
```

### 备份数据

```bash
# 使用管理脚本备份
./docker-manage.sh
# 选择选项 8

# 或手动备份
cd /opt/car-detect
tar -czf backup_$(date +%Y%m%d).tar.gz data/ static/upload/ .env
```

### 清理资源

```bash
# 清理未使用的镜像、容器、网络
docker system prune -f

# 清理所有未使用的卷
docker volume prune -f

# 查看磁盘使用
docker system df
```

---

## 🔍 故障排查

### 问题1：容器无法启动

```bash
# 查看详细日志
docker compose logs

# 检查端口占用
sudo lsof -i :8000

# 检查Docker服务状态
sudo systemctl status docker
```

### 问题2：无法访问服务

```bash
# 检查容器是否运行
docker compose ps

# 检查防火墙
sudo ufw status
sudo ufw allow 8000/tcp

# 测试本地访问
curl http://localhost:8000/health
```

### 问题3：文件上传失败

```bash
# 检查目录权限
ls -la static/upload/
chmod -R 755 static/upload/

# 检查磁盘空间
df -h

# 检查文件大小限制
cat .env | grep MAX_FILE_SIZE
```

### 问题4：数据库错误

```bash
# 检查数据库文件
ls -la data/sensor.db

# 重建数据库
docker compose down
rm data/sensor.db
docker compose up -d
```

---

## 🔄 更新部署

### 方法一：使用管理脚本

```bash
./docker-manage.sh
# 选择选项 6（更新部署）
```

### 方法二：手动更新

```bash
cd /opt/car-detect

# 上传新代码
rsync -avz local-path/ root@server:/opt/car-detect/

# 重新构建并启动
docker compose up -d --build

# 查看日志确认
docker compose logs -f
```

---

## 📈 性能优化

### 1. 调整Worker数量

编辑 `Dockerfile`：

```dockerfile
# 根据CPU核心数调整
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 资源配置

编辑 `docker-compose.yml`：

```yaml
deploy:
  resources:
    limits:
      memory: 4G      # 根据服务器内存调整
      cpus: '4.0'     # 根据CPU核心数调整
```

### 3. 启用缓存

```bash
# 使用BuildKit加速构建
export DOCKER_BUILDKIT=1
docker compose build
```

---

## 🛡️ 安全建议

### 1. 修改默认端口

```env
# .env文件
APP_PORT=8888  # 改为非标准端口
```

### 2. 配置防火墙

```bash
# 只允许必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 3. 定期更新

```bash
# 更新基础镜像
docker pull python:3.11-slim

# 重新构建
docker compose up -d --build
```

---

## 📞 技术支持

### 常用检查命令

```bash
# 检查Docker版本
docker --version
docker compose version

# 检查容器状态
docker compose ps

# 检查网络连接
docker network ls
docker network inspect car-detect_car-detect-network

# 检查卷
docker volume ls
```

### 获取帮助

- 📖 查看完整日志：`docker compose logs -f`
- 📖 进入容器调试：`docker exec -it car-detect-app bash`
- 📖 查看API文档：http://YOUR_SERVER_IP:8000/docs

---

**祝您部署顺利！** 🎉
