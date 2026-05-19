# 🚗 智检慧眼 - 车辆智能检测系统

> AI驱动的车辆智能检测系统，支持车主自检、快速定损、社区巡检三大场景

## ✨ 功能特性

- 📸 **智能图像识别**：基于YOLO的目标检测技术
- 🤖 **AI报告生成**：自动生成专业的车辆检测报告
- 🌐 **现代化界面**：响应式设计，支持PC和移动端
- 🔌 **RESTful API**：标准化接口，易于集成和扩展
- 📊 **数据持久化**：SQLite数据库存储检测记录
- 📝 **完整日志**：结构化日志系统，便于问题排查

## 📦 项目结构

```
car_detect/
├── main.py               # FastAPI主程序
├── config.py             # 全局配置
├── requirements.txt      # Python依赖
├── .env.example          # 环境配置示例
├── deploy.sh             # Linux部署脚本
├── start.bat             # Windows启动脚本
├── static/               # 前端静态资源
│   ├── index.html        # 主页面
│   ├── history.html      # 历史记录页
│   ├── css/style.css     # 样式文件
│   ├── js/main.js        # 交互逻辑
│   └── upload/           # 上传目录
├── sensor/               # 传感器模块
│   └── sensor_api.py     # 图像上传接口
├── models/               # AI模型模块
│   ├── yolo_detect.py    # YOLO检测（预留）
│   ├── qwen_report.py    # 报告生成（预留）
│   ├── model_router.py   # 模型路由
│   └── database.py       # 数据库模型
├── utils/                # 工具模块
│   ├── logger.py         # 日志系统
│   └── validator.py      # 数据校验
├── data/                 # 数据存储
│   └── sensor.db         # SQLite数据库
└── logs/                 # 运行日志
```

## 🚀 快速开始

### 🐳 方式零：Docker部署（推荐，最简单）

**前提条件**：服务器已安装Docker

```bash
# 1. 修改部署脚本中的服务器IP
nano docker-deploy.sh
# 修改: SERVER_HOST="your-server-ip"

# 2. 一键部署
chmod +x docker-deploy.sh
./docker-deploy.sh

# 3. 访问系统
http://YOUR_SERVER_IP:8000
```

📖 **详细文档**: [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md) | [DOCKER_QUICK_REF.md](DOCKER_QUICK_REF.md)

---

### 方式一：Windows本地开发

1. **双击运行启动脚本**
   ```bash
   start.bat
   ```

2. **访问系统**
   - 主页：http://127.0.0.1:8000
   - API文档：http://127.0.0.1:8000/docs

### 方式二：Linux服务器部署

1. **上传项目到服务器**
   ```bash
   scp -r car_detect user@server:/opt/
   cd /opt/car_detect
   ```

2. **执行部署脚本**
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

3. **访问系统**
   ```
   http://YOUR_SERVER_IP:8000
   ```

### 方式三：手动安装

1. **安装Python依赖**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑.env文件，修改配置
   ```

3. **启动服务**
   ```bash
   python main.py
   # 或
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## ⚙️ 配置说明

编辑 `.env` 文件修改配置：

```env
# 项目配置
PROJECT_NAME=智检慧眼
API_PREFIX=/api/v1

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 文件上传限制
MAX_FILE_SIZE=10485760  # 10MB

# 日志级别
LOG_LEVEL=INFO
```

## 📡 API接口

### 核心接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/sensor/upload` | POST | 上传图片 |
| `/api/v1/models/detect` | POST | 车辆检测 |
| `/api/v1/models/damage-assessment` | POST | 快速定损（预留） |
| `/api/v1/models/patrol` | POST | 社区巡检（预留） |
| `/health` | GET | 健康检查 |

### 使用示例

```bash
# 车辆检测
curl -X POST "http://localhost:8000/api/v1/models/detect" \
  -F "file=@car.jpg" \
  -F "vehicle_type=sedan"
```

详细API文档请访问：http://localhost:8000/docs

## 🔧 生产环境部署

### Nginx反向代理配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件缓存
    location /static {
        alias /opt/car_detect/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### HTTPS配置（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🛠️ 常见问题

### 1. 端口被占用

```bash
# 查看占用端口的进程
lsof -i :8000  # Linux
netstat -ano | findstr :8000  # Windows

# 修改端口
# 编辑 .env 文件，修改 PORT 配置
```

### 2. 权限问题

```bash
# Linux下赋予执行权限
chmod +x deploy.sh
chmod -R 755 static/upload
```

### 3. 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 📈 后续扩展

- [ ] 接入真实YOLOv8模型
- [ ] 集成通义千问API生成报告
- [ ] 用户认证系统（JWT）
- [ ] 微信小程序支持
- [ ] 数据统计看板
- [ ] 批量检测功能

## 📄 许可证

MIT License

## 👥 技术支持

如有问题，请提交Issue或联系开发团队。

---

**智检慧眼** - 让车辆检测更智能、更便捷 🚀
