# 🐳 Docker部署 - 快速参考卡片

## ⚡ 30秒快速部署

```bash
# 1. 修改配置（只需改IP）
nano docker-deploy.sh
# 修改: SERVER_HOST="your-server-ip"

# 2. 执行部署
chmod +x docker-deploy.sh
./docker-deploy.sh

# 3. 访问系统
http://YOUR_SERVER_IP:8000
```

---

## 📋 常用命令速查

### 本地操作

```bash
# 一键部署到服务器
./docker-deploy.sh

# 打包项目
./package.sh
```

### 服务器操作

```bash
# 进入项目目录
cd /opt/car-detect

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 启动服务
docker compose up -d

# 更新部署
docker compose up -d --build

# 进入容器
docker exec -it car-detect-app bash
```

### 使用管理脚本

```bash
# 运行交互式管理菜单
./docker-manage.sh
```

---

## 🔧 配置文件位置

| 文件 | 用途 | 路径 |
|------|------|------|
| `.env` | 环境变量 | `/opt/car-detect/.env` |
| `docker-compose.yml` | 容器配置 | `/opt/car-detect/docker-compose.yml` |
| `Dockerfile` | 镜像构建 | `/opt/car-detect/Dockerfile` |

---

## 📁 数据持久化

| 类型 | 宿主机路径 | 容器路径 |
|------|-----------|---------|
| 上传文件 | `./static/upload` | `/app/static/upload` |
| 数据库 | `./data` | `/app/data` |
| 日志 | `./logs` | `/app/logs` |

---

## 🌐 访问地址

- **主页**: http://YOUR_SERVER_IP:8000
- **API文档**: http://YOUR_SERVER_IP:8000/docs
- **健康检查**: http://YOUR_SERVER_IP:8000/health

---

## 🔍 故障排查

```bash
# 检查容器状态
docker compose ps

# 查看详细日志
docker compose logs

# 检查端口占用
sudo lsof -i :8000

# 测试本地访问
curl http://localhost:8000/health

# 检查磁盘空间
df -h

# 清理资源
docker system prune -f
```

---

## 🔄 更新流程

```bash
# 1. 上传新代码
rsync -avz . root@server:/opt/car-detect/

# 2. SSH登录
ssh root@server
cd /opt/car-detect

# 3. 重新构建
docker compose up -d --build

# 4. 验证
docker compose logs -f
```

---

## 💾 备份恢复

```bash
# 备份
tar -czf backup_$(date +%Y%m%d).tar.gz data/ static/upload/ .env

# 恢复
tar -xzf backup_YYYYMMDD.tar.gz
docker compose restart
```

---

## 📞 快速帮助

```bash
# 查看Docker版本
docker --version
docker compose version

# 查看容器资源使用
docker stats car-detect-app

# 查看网络
docker network ls

# 查看卷
docker volume ls
```

---

**更多详细信息请查看**: [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)
