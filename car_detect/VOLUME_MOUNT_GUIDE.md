# 📦 Docker 卷挂载部署说明

> 本文档详细说明智检慧眼系统采用的 Docker 卷挂载部署方式

---

## 🎯 什么是卷挂载部署？

卷挂载部署是将项目代码通过 Docker 卷（Volume）挂载到容器中，而不是将代码复制到镜像内部。这种方式带来了显著的部署效率提升和开发便利性。

---

## 🔄 传统方式 vs 卷挂载方式

### 传统方式（已废弃）

```dockerfile
# Dockerfile
COPY . .  # 将所有代码复制到镜像中
```

**缺点：**
- ❌ 每次代码更新都需要重新构建镜像（耗时 2-5 分钟）
- ❌ 每个版本都会产生新的镜像，占用大量磁盘空间
- ❌ 调试困难，无法实时查看代码变化
- ❌ 部署流程复杂：修改代码 → 上传 → 构建镜像 → 重启容器

### 卷挂载方式（当前使用）

```yaml
# docker-compose.yml
volumes:
  - .:/app  # 将宿主机当前目录挂载到容器 /app
```

**优点：**
- ✅ 代码更新只需重启容器（耗时 5-10 秒）
- ✅ 无需存储多个镜像版本，节省磁盘空间
- ✅ 代码修改立即生效，便于调试
- ✅ 部署流程简化：修改代码 → 上传 → 重启容器

---

## 📂 卷挂载结构

### 完整卷配置

```yaml
volumes:
  # 1. 代码卷挂载（核心改动）
  - .:/app
  
  # 2. 数据持久化卷
  - ./static/upload:/app/static/upload  # 上传文件
  - ./data:/app/data                     # 数据库
  - ./logs:/app/logs                     # 日志文件
```

### 目录映射关系

```
宿主机 (/opt/car-detect/)          容器 (/app/)
├── main.py                    →   ├── main.py
├── models/                    →   ├── models/
│   ├── database.py            →   │   ├── database.py
│   └── yolo_engine.py         →   │   └── yolo_engine.py
├── static/                    →   ├── static/
│   ├── index.html             →   │   ├── index.html
│   └── upload/                →   │   └── upload/        ← 持久化
├── data/                      →   ├── data/              ← 持久化
│   └── sensor.db              →   │   └── sensor.db
└── logs/                      →   ├── logs/              ← 持久化
    └── app.log                →   │   └── app.log
```

**重要说明：**
- 代码卷（`.:/app`）：双向同步，宿主机修改立即反映到容器
- 数据卷（upload、data、logs）：独立持久化，容器删除后数据不丢失

---

## 🚀 部署流程

### 首次部署

```bash
# 1. 上传代码到服务器
./docker-deploy.sh

# 2. 脚本自动执行：
#    - 检测是否首次部署
#    - 构建基础镜像（仅安装依赖）
#    - 启动容器并挂载代码卷
#    - 验证服务状态
```

**首次部署时间：** 约 2-3 分钟（主要是下载依赖和构建镜像）

### 代码更新

```bash
# 方法1：使用自动化脚本（推荐）
./docker-deploy.sh
# 脚本检测到镜像已存在，跳过构建，仅上传代码并重启

# 方法2：手动更新
cd /opt/car-detect
rsync -avz local-code/ .
docker compose restart

# 方法3：使用管理脚本
./docker-manage.sh
# 选择选项 6（更新部署）
```

**代码更新时间：** 约 5-10 秒（仅重启容器）

---

## 🔧 常见操作

### 查看卷挂载状态

```bash
# 查看容器详细信息
docker inspect car-detect-app | grep -A 10 Mounts

# 查看卷列表
docker volume ls

# 查看容器挂载点
docker inspect car-detect-app --format='{{json .Mounts}}' | python -m json.tool
```

### 验证代码同步

```bash
# 在宿主机修改代码
echo "# Test" >> /opt/car-detect/test.txt

# 在容器中验证
docker exec car-detect-app cat /app/test.txt
# 输出: # Test
```

### 重启容器使代码生效

```bash
# 重启单个容器
docker compose restart

# 或重启所有服务
docker compose down
docker compose up -d
```

---

## 💡 最佳实践

### 1. 何时需要重新构建镜像？

**需要重新构建的情况：**
- ✅ 修改了 `requirements.txt`（新增或删除依赖）
- ✅ 修改了 `Dockerfile` 本身
- ✅ 首次部署或迁移到新服务器

**无需重新构建的情况：**
- ✅ 修改 Python 代码（`.py` 文件）
- ✅ 修改 HTML/CSS/JS 文件
- ✅ 修改配置文件（`.env` 除外）

### 2. 依赖更新流程

```bash
# 1. 修改 requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# 2. 重新构建镜像
docker compose build

# 3. 重启容器
docker compose up -d
```

### 3. 数据备份

```bash
# 备份数据卷（不包括代码）
tar -czf backup_$(date +%Y%m%d).tar.gz \
    data/ \
    static/upload/ \
    logs/ \
    .env
```

---

## 🔍 故障排查

### 问题1：代码修改未生效

**症状：** 修改代码后，访问服务仍显示旧内容

**原因：** 容器未重启

**解决：**
```bash
docker compose restart
```

### 问题2：卷挂载失败

**症状：** 容器启动失败，报错 "mount path not found"

**原因：** 宿主机路径不存在或权限不足

**解决：**
```bash
# 检查目录是否存在
ls -la /opt/car-detect/

# 修复权限
chmod -R 755 /opt/car-detect/

# 重新启动
docker compose up -d
```

### 问题3：数据丢失

**症状：** 重启容器后，上传的文件或数据库记录消失

**原因：** 数据卷未正确挂载

**解决：**
```bash
# 检查 docker-compose.yml 中的卷配置
cat docker-compose.yml | grep -A 5 volumes

# 确保包含以下配置：
# - ./static/upload:/app/static/upload
# - ./data:/app/data
# - ./logs:/app/logs
```

### 问题4：性能问题

**症状：** 容器运行缓慢，I/O 延迟高

**原因：** 卷挂载过多或文件系统性能问题

**解决：**
```bash
# 查看容器资源使用
docker stats car-detect-app

# 优化卷挂载（仅挂载必要目录）
# 避免挂载 node_modules、venv 等大型目录
```

---

## 📊 性能对比

### 部署时间对比

| 操作 | 传统方式 | 卷挂载方式 | 提升 |
|------|---------|-----------|------|
| 首次部署 | 3-5 分钟 | 3-5 分钟 | 相同 |
| 代码更新 | 2-5 分钟 | 5-10 秒 | **95%** ⚡ |
| 依赖更新 | 2-5 分钟 | 2-5 分钟 | 相同 |
| 回滚版本 | 1-2 分钟 | 5-10 秒 | **90%** ⚡ |

### 磁盘空间对比

| 项目 | 传统方式 | 卷挂载方式 | 节省 |
|------|---------|-----------|------|
| 基础镜像 | ~500MB | ~500MB | - |
| 每版本镜像 | ~500MB | 0MB | **100%** 💾 |
| 10个版本总计 | ~5.5GB | ~500MB | **91%** 💾 |

---

## 🛡️ 安全注意事项

### 1. 敏感文件排除

使用 `.dockerignore` 排除敏感文件：

```
.env
*.db
__pycache__/
*.pyc
.git/
venv/
```

### 2. 权限控制

```bash
# 设置合理的文件权限
chmod -R 755 /opt/car-detect/
chmod 600 /opt/car-detect/.env

# 确保 Docker 以非 root 用户运行（可选）
# 在 docker-compose.yml 中添加：
# user: "1000:1000"
```

### 3. 网络安全

```bash
# 限制端口访问
sudo ufw allow from 192.168.1.0/24 to any port 8000

# 或使用 Nginx 反向代理 + HTTPS
```

---

## 📞 技术支持

### 常用诊断命令

```bash
# 查看容器状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 进入容器调试
docker exec -it car-detect-app bash

# 检查卷挂载
docker inspect car-detect-app --format='{{json .Mounts}}'

# 查看资源使用
docker stats car-detect-app

# 清理无用资源
docker system prune -f
```

### 相关文档

- 📘 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - 完整部署指南
- 📗 [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md) - 快速参考
- 📙 [README.md](README.md) - 项目总览

---

**卷挂载部署让开发和运维更高效！** 🎉
