# ✅ 部署完成 - 智检慧眼系统

## 🎉 恭喜！系统已成功部署到您的Ubuntu服务器

---

## 📊 部署信息

| 项目 | 详情 |
|------|------|
| **服务器** | yan (root@kk-0o6x1c1fjjohyl8935je) |
| **部署路径** | /opt/car-detect |
| **容器名称** | car-detect-app |
| **容器状态** | ✅ Up (healthy) |
| **端口映射** | 0.0.0.0:8000 -> 8000/tcp |
| **Docker版本** | 29.4.3 |
| **Docker Compose** | v5.1.3 |
| **部署时间** | 2026-05-19 15:36 |

---

## 🌐 访问地址

### Web界面
- **主页**: `http://YOUR_SERVER_IP:8000`
- **历史记录**: `http://YOUR_SERVER_IP:8000/history.html`

### API接口
- **API文档**: `http://YOUR_SERVER_IP:8000/docs`
- **健康检查**: `http://YOUR_SERVER_IP:8000/health`
- **ReDoc文档**: `http://YOUR_SERVER_IP:8000/redoc`

---

## 🔧 管理命令

### 快速管理（推荐）

```bash
# SSH登录服务器
ssh yan

# 进入项目目录
cd /opt/car-detect

# 运行交互式管理菜单
./docker-manage.sh
```

管理菜单提供：
1. 查看容器状态
2. 查看实时日志
3. 重启服务
4. 停止服务
5. 启动服务
6. 更新部署
7. 进入容器
8. 备份数据
9. 清理资源

### Docker Compose命令

```bash
# 查看容器状态
ssh yan "cd /opt/car-detect && docker compose ps"

# 查看实时日志
ssh yan "cd /opt/car-detect && docker compose logs -f"

# 重启服务
ssh yan "cd /opt/car-detect && docker compose restart"

# 停止服务
ssh yan "cd /opt/car-detect && docker compose down"

# 启动服务
ssh yan "cd /opt/car-detect && docker compose up -d"

# 更新部署（代码修改后）
ssh yan "cd /opt/car-detect && docker compose up -d --build"

# 进入容器
ssh yan "docker exec -it car-detect-app bash"

# 查看资源使用
ssh yan "docker stats car-detect-app"
```

---

## 📁 目录结构

```
/opt/car-detect/
├── main.py                    # FastAPI主程序
├── config.py                  # 配置文件
├── requirements.txt           # Python依赖
├── .env                       # 环境变量
├── docker-compose.yml         # Docker编排配置
├── Dockerfile                 # Docker镜像定义
├── docker-manage.sh           # 管理脚本
│
├── static/
│   ├── index.html             # 主页
│   ├── history.html           # 历史记录页
│   ├── css/style.css          # 样式文件
│   ├── js/main.js             # 交互逻辑
│   └── upload/                # 上传文件目录（持久化）
│
├── sensor/                    # 传感器模块
├── models/                    # AI模型模块
├── utils/                     # 工具模块
│
├── data/                      # 数据库目录（持久化）
│   └── sensor.db              # SQLite数据库
│
└── logs/                      # 日志目录（持久化）
    └── app_YYYY-MM-DD.log     # 按天切割的日志
```

---

## 🔍 验证部署

### 1. 检查容器状态

```bash
ssh yan "cd /opt/car-detect && docker compose ps"
```

应该看到：
```
NAME             STATUS         PORTS
car-detect-app   Up (healthy)   0.0.0.0:8000->8000/tcp
```

### 2. 测试健康检查

```bash
curl http://YOUR_SERVER_IP:8000/health
```

应该返回：
```json
{
  "status": "healthy",
  "service": "智检慧眼",
  "version": "1.0.0"
}
```

### 3. 访问Web界面

在浏览器中打开 `http://YOUR_SERVER_IP:8000`，应该看到：
- ✅ 现代化的渐变UI界面
- ✅ 图片上传区域
- ✅ 车辆类型选择
- ✅ 检测按钮

### 4. 测试图片上传

1. 点击或拖拽上传一张车辆图片
2. 选择车辆类型
3. 点击"开始检测"
4. 查看检测结果和报告

---

## 📝 配置说明

### 环境变量 (.env)

当前配置：
```env
PROJECT_NAME=智检慧眼
API_PREFIX=/api/v1
MAX_FILE_SIZE=10485760  # 10MB
LOG_LEVEL=INFO
```

修改配置后需要重启容器：
```bash
ssh yan "cd /opt/car-detect && docker compose restart"
```

### 数据持久化

以下数据已配置持久化，容器重建后不会丢失：

| 类型 | 宿主机路径 | 容器路径 |
|------|-----------|---------|
| 上传文件 | `./static/upload` | `/app/static/upload` |
| 数据库 | `./data` | `/app/data` |
| 日志 | `./logs` | `/app/logs` |

---

## 🔐 安全建议

### 1. 配置防火墙

```bash
# 如果服务器启用了UFW防火墙
ssh yan "sudo ufw allow 8000/tcp"
ssh yan "sudo ufw reload"
```

### 2. 修改默认端口（可选）

编辑 `.env` 文件：
```env
APP_PORT=8888  # 改为其他端口
```

然后重启：
```bash
ssh yan "cd /opt/car-detect && docker compose down && docker compose up -d"
```

### 3. 配置域名和HTTPS（推荐）

参考 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) 中的Nginx配置章节。

---

## 🔄 更新部署

### 方法一：使用管理脚本

```bash
ssh yan
cd /opt/car-detect
./docker-manage.sh
# 选择选项 6（更新部署）
```

### 方法二：手动更新

```bash
# 1. 上传新代码
scp -r * yan:/opt/car-detect/

# 2. SSH登录并重新构建
ssh yan "cd /opt/car-detect && docker compose up -d --build"

# 3. 查看日志确认
ssh yan "cd /opt/car-detect && docker compose logs -f"
```

---

## 💾 备份数据

### 使用管理脚本

```bash
ssh yan
cd /opt/car-detect
./docker-manage.sh
# 选择选项 8（备份数据）
```

### 手动备份

```bash
ssh yan "cd /opt/car-detect && tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz data/ static/upload/ .env"
```

备份文件保存在 `/opt/car-detect/` 目录下。

---

## 📊 监控和维护

### 查看日志

```bash
# 实时日志
ssh yan "cd /opt/car-detect && docker compose logs -f"

# 最近100行
ssh yan "cd /opt/car-detect && docker compose logs --tail=100"

# 仅错误日志
ssh yan "cd /opt/car-detect && docker compose logs | grep ERROR"

# 导出日志
ssh yan "cd /opt/car-detect && docker compose logs > app_$(date +%Y%m%d).log"
```

### 查看资源使用

```bash
# CPU和内存使用
ssh yan "docker stats car-detect-app"

# 磁盘使用
ssh yan "docker system df"
```

### 清理资源

```bash
# 清理未使用的镜像、容器、网络
ssh yan "docker system prune -f"

# 清理所有未使用的卷
ssh yan "docker volume prune -f"
```

---

## ❓ 故障排查

### 问题1：无法访问服务

```bash
# 检查容器状态
ssh yan "cd /opt/car-detect && docker compose ps"

# 检查端口占用
ssh yan "sudo lsof -i :8000"

# 检查防火墙
ssh yan "sudo ufw status"

# 测试本地访问
ssh yan "curl http://localhost:8000/health"
```

### 问题2：容器不断重启

```bash
# 查看详细日志
ssh yan "cd /opt/car-detect && docker compose logs --tail=100"

# 常见原因：
# - 代码错误
# - 端口被占用
# - 权限问题
```

### 问题3：文件上传失败

```bash
# 检查目录权限
ssh yan "ls -la /opt/car-detect/static/upload/"
ssh yan "chmod -R 755 /opt/car-detect/static/upload/"

# 检查磁盘空间
ssh yan "df -h"
```

### 问题4：数据库错误

```bash
# 检查数据库文件
ssh yan "ls -la /opt/car-detect/data/"

# 重建数据库（会丢失数据）
ssh yan "cd /opt/car-detect && rm data/sensor.db && docker compose restart"
```

---

## 📞 获取帮助

### 文档索引

- 📘 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) - 完整Docker部署指南
- 📗 [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md) - 快速参考卡片
- 📙 [README.md](README.md) - 项目总览
- 📕 [SSH_DEPLOY_GUIDE.md](SSH_DEPLOY_GUIDE.md) - SSH部署指南

### 联系支持

如遇到问题：
1. 查看日志：`docker compose logs -f`
2. 查阅文档：上述文档列表
3. 检查配置：`.env` 文件和 `docker-compose.yml`

---

## ✅ 部署检查清单

请确认以下项目：

- [x] Docker容器正常运行
- [x] 健康检查通过
- [x] 端口8000已映射
- [x] 数据目录已持久化
- [x] 管理脚本已上传
- [ ] 防火墙已配置（如需要）
- [ ] 域名已配置（如需要）
- [ ] HTTPS已配置（如需要）

---

## 🎊 下一步

1. **立即体验**：
   - 访问 http://YOUR_SERVER_IP:8000
   - 上传测试图片
   - 查看检测结果

2. **配置域名**（可选）：
   - 参考 DOCKER_DEPLOY.md
   - 设置Nginx反向代理
   - 配置Let's Encrypt SSL证书

3. **集成AI模型**（可选）：
   - 接入YOLOv8进行真实检测
   - 集成通义千问生成专业报告

4. **监控系统**（推荐）：
   - 设置日志轮转
   - 配置告警通知
   - 定期备份数据

---

**祝您使用愉快！** 🚀

*部署完成时间: 2026-05-19 15:36*  
*容器状态: Up (healthy)*  
*下次检查: 建议每天查看一次日志和容器状态*
