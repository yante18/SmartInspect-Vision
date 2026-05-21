# 🚀 快速开始 - 卷挂载部署

> 5 分钟快速了解如何使用新的 Docker 卷挂载部署方式

---

## 📌 什么是卷挂载部署？

**简单来说：** 项目代码不再复制到 Docker 镜像中，而是通过"快捷方式"（卷挂载）让容器直接访问服务器上的代码文件。

**好处：**
- ⚡ 代码更新后只需重启容器（5-10 秒）
- 💾 不占用额外磁盘空间存储多个镜像版本
- 🔧 调试方便，修改代码立即生效

---

## 🎯 核心概念

### 传统方式 vs 卷挂载方式

```
传统方式：
本地代码 → 上传到服务器 → 复制到镜像 → 构建镜像 → 启动容器
         （每次更新都要重新走完整流程，耗时 2-5 分钟）

卷挂载方式：
本地代码 → 上传到服务器 → 重启容器
         （代码通过卷挂载，容器直接读取，耗时 5-10 秒）
```

### 卷挂载结构

```
服务器目录: /opt/car-detect/
    ├── main.py  ──────────┐
    ├── models/            │
    │   └── *.py           │  卷挂载 (.:/app)
    ├── static/            │
    │   └── upload/  ──────┼──→ 容器内: /app/
    ├── data/        ──────┤       ├── main.py
    └── logs/        ──────┘       ├── models/
                                   ├── static/upload/
                                   ├── data/
                                   └── logs/
```

---

## 🚀 快速上手

### 首次部署（3 分钟）

```bash
# 1. 在本地修改部署脚本中的服务器 IP
nano docker-deploy.sh
# 修改: SERVER_HOST="your-server-ip"

# 2. 执行一键部署
chmod +x docker-deploy.sh
./docker-deploy.sh

# 3. 等待部署完成，访问系统
# http://YOUR_SERVER_IP:8000
```

**发生了什么：**
1. ✅ 测试 SSH 连接
2. ✅ 上传项目文件到服务器
3. ✅ 构建 Docker 镜像（仅安装依赖，不包含代码）
4. ✅ 启动容器并挂载代码卷
5. ✅ 验证服务状态

---

### 代码更新（10 秒钟）

#### 方法 1：使用自动化脚本（推荐）

```bash
# 在本地执行
./docker-deploy.sh

# 脚本会自动：
# - 检测镜像已存在，跳过构建
# - 上传最新代码
# - 重启容器
```

#### 方法 2：手动更新

```bash
# 1. 上传新代码
rsync -avz . root@your-server-ip:/opt/car-detect/

# 2. SSH 登录并重启
ssh root@your-server-ip
cd /opt/car-detect
docker compose restart
```

#### 方法 3：使用管理脚本

```bash
# SSH 登录服务器
ssh root@your-server-ip
cd /opt/car-detect

# 运行管理脚本
./docker-manage.sh
# 选择选项 6（更新部署）
```

---

## 📋 常用操作速查

### 查看服务状态

```bash
# SSH 登录服务器
ssh root@your-server-ip
cd /opt/car-detect

# 查看容器状态
docker compose ps

# 查看实时日志
docker compose logs -f
```

### 重启服务

```bash
# 代码修改后重启使生效
docker compose restart
```

### 停止/启动服务

```bash
# 停止
docker compose down

# 启动
docker compose up -d
```

### 进入容器

```bash
docker exec -it car-detect-app bash
```

---

## ❓ 常见问题

### Q1: 什么时候需要重新构建镜像？

**需要重新构建：**
- ✅ 修改了 `requirements.txt`（添加或删除 Python 包）
- ✅ 修改了 `Dockerfile` 本身
- ✅ 首次部署或迁移到新服务器

**无需重新构建：**
- ✅ 修改 Python 代码（`.py` 文件）
- ✅ 修改 HTML/CSS/JavaScript 文件
- ✅ 修改配置文件（除了 `.env`）

### Q2: 代码修改后为什么没生效？

**原因：** 容器还在运行旧代码

**解决：** 重启容器
```bash
docker compose restart
```

### Q3: 如何验证卷挂载是否成功？

```bash
# 方法 1：查看容器挂载信息
docker inspect car-detect-app --format='{{json .Mounts}}' | python -m json.tool

# 方法 2：测试文件同步
echo "test" > /opt/car-detect/test.txt
docker exec car-detect-app cat /app/test.txt
# 应该输出: test
```

### Q4: 数据会丢失吗？

**不会！** 数据卷独立于代码卷：
- `./static/upload` - 上传的文件
- `./data` - 数据库
- `./logs` - 日志文件

即使删除容器，这些数据也不会丢失。

### Q5: 性能会变差吗？

**不会！** 卷挂载的性能与直接访问文件系统几乎相同。对于 Web 应用来说，性能差异可以忽略不计。

---

## 🔧 故障排查

### 问题 1：容器无法启动

```bash
# 查看详细日志
docker compose logs

# 检查端口占用
sudo lsof -i :8000

# 检查 Docker 服务状态
sudo systemctl status docker
```

### 问题 2：无法访问服务

```bash
# 检查容器是否运行
docker compose ps

# 检查防火墙
sudo ufw status
sudo ufw allow 8000/tcp

# 测试本地访问
curl http://localhost:8000/health
```

### 问题 3：代码修改未生效

```bash
# 确认文件已上传
ls -la /opt/car-detect/main.py

# 重启容器
docker compose restart

# 查看日志确认
docker compose logs -f
```

---

## 📊 性能对比

| 操作 | 传统方式 | 卷挂载方式 | 提升 |
|------|---------|-----------|------|
| 首次部署 | 3-5 分钟 | 3-5 分钟 | 相同 |
| **代码更新** | 2-5 分钟 | **5-10 秒** | **95%** ⚡ |
| 依赖更新 | 2-5 分钟 | 2-5 分钟 | 相同 |
| 磁盘空间（10版本） | ~5.5GB | **~500MB** | **91%** 💾 |

---

## 📚 更多文档

- 📘 [VOLUME_MOUNT_GUIDE.md](VOLUME_MOUNT_GUIDE.md) - 卷挂载详细说明
- 📗 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - 完整部署指南
- 📙 [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) - 迁移总结
- 📕 [CHANGELOG.md](CHANGELOG.md) - 变更日志

---

## 🎉 总结

**卷挂载部署的核心要点：**

1. **首次部署**：需要构建镜像（3-5 分钟）
2. **代码更新**：只需重启容器（5-10 秒）⚡
3. **依赖更新**：需要重新构建镜像（2-5 分钟）
4. **数据安全**：数据卷独立，不会丢失

**记住这个公式：**
```
代码更新 = 上传代码 + docker compose restart
```

就是这么简单！🎊
