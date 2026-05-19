# 🚀 SSH一键部署到Ubuntu服务器（Docker版）

## ⚡ 3步完成部署

### 第1步：修改服务器配置

编辑 `docker-deploy.sh` 文件，找到以下配置并修改：

```bash
# 第17-19行左右
SERVER_USER="root"              # 改为您的SSH用户名（通常是root或ubuntu）
SERVER_HOST="your-server-ip"    # 改为您的服务器IP地址（例如：123.456.789.0）
SERVER_PORT="22"                # SSH端口（默认22，如果修改过请改为您设置的端口）
```

**示例**：
```bash
SERVER_USER="ubuntu"
SERVER_HOST="47.123.45.67"
SERVER_PORT="22"
```

---

### 第2步：执行部署脚本

在**本地电脑**的项目目录下打开终端（PowerShell或CMD），运行：

#### Windows用户：
```powershell
# 如果使用Git Bash或WSL
chmod +x docker-deploy.sh
./docker-deploy.sh

# 如果只有PowerShell，可以使用：
bash docker-deploy.sh
```

#### Mac/Linux用户：
```bash
chmod +x docker-deploy.sh
./docker-deploy.sh
```

---

### 第3步：等待部署完成

脚本会自动执行以下操作：

```
✅ 测试SSH连接
✅ 打包项目文件
✅ 上传到服务器 /opt/car-detect
✅ 检查Docker环境
✅ 构建Docker镜像
✅ 启动容器
✅ 验证服务状态
```

部署完成后，您会看到：

```
=========================================
  🎉 部署完成！
=========================================

📍 服务器: root@47.123.45.67
📁 部署路径: /opt/car-detect
🌐 访问地址: http://47.123.45.67:8000
📖 API文档: http://47.123.45.67:8000/docs
```

---

## 🌐 访问系统

部署成功后，在浏览器中访问：

- **主页**: `http://YOUR_SERVER_IP:8000`
- **API文档**: `http://YOUR_SERVER_IP:8000/docs`

---

## 🔧 常用管理命令

### 查看服务状态

```bash
# SSH登录服务器
ssh root@YOUR_SERVER_IP

# 进入项目目录
cd /opt/car-detect

# 查看容器状态
docker compose ps
```

### 查看日志

```bash
# 实时日志
docker compose logs -f

# 最近100行
docker compose logs --tail=100
```

### 重启服务

```bash
docker compose restart
```

### 停止服务

```bash
docker compose down
```

### 更新代码

```bash
# 重新上传代码后
docker compose up -d --build
```

---

## 📱 使用交互式管理菜单（推荐）

上传管理脚本到服务器：

```bash
scp docker-manage.sh root@YOUR_SERVER_IP:/opt/car-detect/
```

SSH登录服务器后运行：

```bash
ssh root@YOUR_SERVER_IP
cd /opt/car-detect
chmod +x docker-manage.sh
./docker-manage.sh
```

管理菜单提供：
- ✅ 查看容器状态
- ✅ 查看实时日志
- ✅ 重启/停止/启动服务
- ✅ 更新部署
- ✅ 进入容器
- ✅ 备份数据
- ✅ 清理资源

---

## ❓ 常见问题

### Q1: SSH连接失败？

**错误信息**: `Connection timed out` 或 `Connection refused`

**解决方案**：
1. 检查服务器IP是否正确
2. 检查SSH端口是否正确（默认22）
3. 检查服务器防火墙是否开放SSH端口
4. 首次连接可能需要手动确认指纹：
   ```bash
   ssh root@YOUR_SERVER_IP
   # 输入 yes 确认
   ```

### Q2: Docker未安装？

**错误信息**: `Docker未安装，请先安装Docker`

**解决方案**：
在服务器上安装Docker：
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker compose version
```

### Q3: 端口被占用？

**错误信息**: `Address already in use`

**解决方案**：
```bash
# 查看占用端口的进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 <PID>

# 或者修改端口
# 编辑 .env 文件，修改 APP_PORT=8080
```

### Q4: 无法访问服务？

**检查清单**：
1. 容器是否正常运行：`docker compose ps`
2. 防火墙是否开放端口：`sudo ufw allow 8000/tcp`
3. 健康检查是否通过：`curl http://localhost:8000/health`

---

## 📊 系统要求

### 服务器配置
- **操作系统**: Ubuntu 20.04 / 22.04 LTS
- **CPU**: 1核及以上
- **内存**: 1GB及以上（推荐2GB+）
- **磁盘**: 10GB可用空间
- **网络**: 已开放8000端口

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: V2.x

---

## 🔐 安全建议

### 1. 配置防火墙

```bash
# Ubuntu UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # 应用
sudo ufw enable
```

### 2. 修改默认端口

编辑 `.env` 文件：
```env
APP_PORT=8888  # 改为非标准端口
```

### 3. 配置域名和HTTPS

参考 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) 的Nginx配置章节。

---

## 📞 获取帮助

### 查看详细文档

- 📘 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - 完整部署指南（475行）
- 📗 [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md) - 快速参考卡片
- 📙 [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) - 部署总结

### 检查日志

```bash
# 查看容器日志
docker compose logs -f

# 查看特定时间段的日志
docker compose logs --since="2024-01-01T00:00:00"

# 导出日志
docker compose logs > app.log
```

### 进入容器调试

```bash
docker exec -it car-detect-app bash
```

---

## ✅ 部署验证清单

部署完成后，请确认：

- [ ] SSH连接成功
- [ ] 项目文件上传到 `/opt/car-detect`
- [ ] Docker镜像构建成功
- [ ] 容器状态为 "Up (healthy)"
- [ ] 可以访问 http://YOUR_SERVER_IP:8000
- [ ] API文档可访问：http://YOUR_SERVER_IP:8000/docs
- [ ] 健康检查返回正常：`curl http://YOUR_SERVER_IP:8000/health`
- [ ] 可以上传图片并看到检测结果

---

**祝您部署顺利！** 🎉

如有问题，请查看详细文档或联系技术支持。
