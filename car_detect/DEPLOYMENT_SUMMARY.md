# 🎯 Docker部署总结 - 智检慧眼系统

## ✅ 已创建的Docker相关文件

### 核心配置文件

| 文件 | 说明 | 用途 |
|------|------|------|
| [Dockerfile](Dockerfile) | Docker镜像构建文件 | 定义应用运行环境 |
| [docker-compose.yml](docker-compose.yml) | 容器编排配置 | 管理多容器应用 |
| [.dockerignore](.dockerignore) | Docker忽略文件 | 优化构建速度 |

### 部署脚本

| 文件 | 说明 | 执行位置 |
|------|------|---------|
| [docker-deploy.sh](docker-deploy.sh) | SSH一键部署脚本 | **本地执行** |
| [docker-manage.sh](docker-manage.sh) | 交互式管理脚本 | **服务器执行** |

### Nginx配置

| 文件 | 说明 |
|------|------|
| [docker-nginx.conf](docker-nginx.conf) | Docker环境Nginx反向代理配置 |

### 文档

| 文件 | 说明 |
|------|------|
| [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) | 完整Docker部署指南（475行） |
| [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md) | 快速参考卡片 |

---

## 🚀 部署流程总览

```
┌─────────────────────────────────────────────────────┐
│                  本地开发环境                         │
│                                                     │
│  1. 修改 docker-deploy.sh 中的服务器配置            │
│     - SERVER_HOST (服务器IP)                        │
│     - SERVER_USER (SSH用户名)                       │
│     - SERVER_PORT (SSH端口)                         │
│                                                     │
│  2. 执行部署脚本                                     │
│     ./docker-deploy.sh                              │
│                                                     │
│  📤 自动上传项目文件到服务器                          │
└──────────────────┬──────────────────────────────────┘
                   │ SSH + SCP
                   ▼
┌─────────────────────────────────────────────────────┐
│               Ubuntu服务器                           │
│                                                     │
│  /opt/car-detect/                                   │
│  ├── Dockerfile              ← 仅安装依赖           │
│  ├── docker-compose.yml      ← 容器编排             │
│  ├── .env                    ← 环境配置             │
│  ├── main.py                 ← 代码(卷挂载)         │
│  ├── models/                 ← 模块(卷挂载)         │
│  ├── static/upload/          ← 上传文件(持久化)     │
│  ├── data/                   ← 数据库(持久化)       │
│  └── logs/                   ← 日志(持久化)         │
│                                                     │
│  🐳 Docker Compose 启动                             │
│  ├── car-detect-app (FastAPI应用)                  │
│  ├── 代码卷挂载: .:/app                            │
│  └── 端口映射: 8000:8000                           │
│                                                     │
│  🌐 访问: http://SERVER_IP:8000                     │
│  ⚡ 代码更新: docker compose restart                │
└─────────────────────────────────────────────────────┘
```

---

## 📋 部署步骤详解

### 第一步：准备阶段（本地）

```bash
# 1. 确保项目文件完整
cd car_detect
ls -la

# 应该看到以下关键文件：
# - Dockerfile
# - docker-compose.yml
# - docker-deploy.sh
# - main.py
# - requirements.txt
# - ...
```

### 第二步：配置服务器信息（本地）

编辑 `docker-deploy.sh`：

```bash
# 修改以下3行
SERVER_USER="root"              # 改为您的SSH用户名
SERVER_HOST="123.456.789.0"    # 改为您的服务器IP
SERVER_PORT="22"                # SSH端口（默认22）
```

### 第三步：执行部署（本地）

```bash
# 赋予执行权限
chmod +x docker-deploy.sh

# 运行部署脚本
./docker-deploy.sh
```

脚本会自动完成：
1. ✅ 测试SSH连接
2. ✅ 打包项目文件
3. ✅ 上传到服务器 `/opt/car-detect`
4. ✅ 在服务器上构建Docker镜像
5. ✅ 启动容器
6. ✅ 验证服务状态

### 第四步：验证部署（浏览器）

```
访问: http://YOUR_SERVER_IP:8000
```

应该看到：
- ✅ 主页正常显示
- ✅ 可以上传图片
- ✅ API文档可访问：http://YOUR_SERVER_IP:8000/docs

---

## 🔧 常用管理操作

### 查看服务状态

```bash
# SSH登录服务器
ssh root@YOUR_SERVER_IP

# 进入项目目录
cd /opt/car-detect

# 查看容器状态
docker compose ps

# 预期输出：
# NAME                STATUS         PORTS
# car-detect-app      Up (healthy)   0.0.0.0:8000->8000/tcp
```

### 查看日志

```bash
# 实时日志
docker compose logs -f

# 最近100行
docker compose logs --tail=100

# 仅错误日志
docker compose logs | grep ERROR
```

### 重启服务

```bash
docker compose restart
```

### 更新代码

**卷挂载方式的优势：**
- ⚡ 无需重新构建镜像
- ⚡ 代码修改立即生效
- ⚡ 部署时间从几分钟缩短到几秒

```bash
# 方法1：使用管理脚本
./docker-manage.sh
# 选择选项 6（更新部署）

# 方法2：手动更新（推荐）
docker compose restart

# 方法3：首次部署或依赖变更时
docker compose up -d --build
```

### 备份数据

```bash
# 使用管理脚本
./docker-manage.sh
# 选择选项 8（备份数据）

# 或手动备份
tar -czf backup_$(date +%Y%m%d).tar.gz data/ static/upload/ .env
```

---

## 📊 资源占用

### 磁盘空间

| 项目 | 大小 |
|------|------|
| Docker镜像 | ~500MB |
| 容器运行 | ~100MB |
| 数据库（初始） | <1MB |
| 上传文件 | 视使用情况 |

**总计**: 约600MB起步

### 内存使用

| 状态 | 内存 |
|------|------|
| 空闲 | ~200MB |
| 正常负载 | ~300-500MB |
| 高负载 | ~800MB-1GB |

### CPU使用

- 空闲: <1%
- 处理请求: 10-30%
- 取决于并发量和检测复杂度

---

## 🌐 网络配置

### 端口映射

```
宿主机:8000 → 容器:8000
```

### 防火墙设置

```bash
# Ubuntu UFW
sudo ufw allow 8000/tcp
sudo ufw reload

# CentOS firewalld
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

### 域名配置（可选）

如果需要绑定域名，参考 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) 的Nginx配置章节。

---

## 🔍 故障排查速查表

| 问题 | 可能原因 | 解决方案 |
|------|---------|----------|
| 容器无法启动 | 端口被占用 | `sudo lsof -i :8000` 检查并释放端口 |
| 无法访问 | 防火墙阻止 | `sudo ufw allow 8000/tcp` |
| 上传失败 | 权限问题 | `chmod -R 755 static/upload` |
| 数据库错误 | 文件损坏 | 删除 `data/sensor.db` 重启 |
| 内存不足 | 资源限制 | 调整 `docker-compose.yml` 中的内存限制 |
| 构建失败 | 网络问题 | 更换pip镜像源或使用VPN |
| 代码修改未生效 | 容器未重启 | `docker compose restart` 重启容器 |
| 卷挂载失败 | 路径错误 | 检查 docker-compose.yml 中的卷路径配置 |

---

## 📈 性能优化建议

### 1. 调整Worker数量

根据CPU核心数调整 `Dockerfile` 中的workers参数：

```dockerfile
# 2核CPU: --workers 2
# 4核CPU: --workers 4
# 8核CPU: --workers 8
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 资源配置

在 `docker-compose.yml` 中调整：

```yaml
deploy:
  resources:
    limits:
      memory: 2G      # 根据服务器内存调整
      cpus: '2.0'     # 根据CPU核心数调整
```

### 3. 启用BuildKit

```bash
export DOCKER_BUILDKIT=1
docker compose build
```

---

## 🔄 持续集成/持续部署（CI/CD）

### GitHub Actions示例（可选）

```yaml
name: Deploy to Server

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/car-detect
            git pull
            docker compose up -d --build
```

---

## 📞 获取帮助

### 文档索引

- 📘 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - 完整部署指南
- 📗 [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md) - 快速参考
- 📙 [README.md](README.md) - 项目总览

### 命令速查

```bash
# 查看所有Docker容器
docker ps -a

# 查看镜像
docker images

# 查看网络
docker network ls

# 查看卷
docker volume ls

# 清理无用资源
docker system prune -f
```

---

## ✅ 部署检查清单

部署完成后，请确认：

- [ ] 可以通过 http://SERVER_IP:8000 访问主页
- [ ] 可以上传图片并看到检测结果
- [ ] API文档可访问：http://SERVER_IP:8000/docs
- [ ] 健康检查返回正常：`curl http://SERVER_IP:8000/health`
- [ ] 容器状态为 "Up (healthy)"
- [ ] 日志正常输出，无ERROR级别错误
- [ ] 数据目录已正确挂载（持久化）
- [ ] 防火墙已开放8000端口

---

**恭喜！您已成功部署智检慧眼系统！** 🎉

如需进一步定制或遇到问题，请参考完整文档或联系技术支持。
