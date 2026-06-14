# 智检慧眼 - 车辆智能检测系统 🚗

AI驱动的车辆损伤智能检测系统，基于YOLOv8和LLM技术，提供车主自检、快速定损、社区巡检功能。

##  主要特性

- 🤖 **AI损伤检测**：基于YOLOv8的车辆损伤自动识别
- 📊 **智能报告生成**：使用LLM生成专业的检测报告
-  **3D模型展示**：支持小米SU7 Max等车型的3D可视化
- 📱 **Web界面**：响应式设计，支持PC和移动端
-  **RESTful API**：完整的API接口支持第三方集成
- 💾 **历史记录**：自动保存所有检测记录

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Windows/Linux/macOS

### 安装步骤

1. **克隆仓库**
```bash
git clone <your-repo-url>
cd SmartInspect-Vision/car_detect
```

2. **启动项目**（Windows）
```bash
.\start.bat
```

或手动启动：
```bash
# 激活虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
```

3. **访问应用**
- 主页：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📁 项目结构

```
car_detect/
├── main.py                 # FastAPI主入口
├── config.py              # 配置管理
├── requirements.txt       # 依赖包
├── .env                  # 环境变量
│
├── models/               # 模型相关
│   ├── database.py       # SQLite数据库
│   ├── model_router.py   # YOLO检测路由
│   ── qwen_report.py    # LLM报告生成
│
├── sensor/               # 传感器API
│   └── sensor_api.py     # 检测记录管理
│
── static/               # 前端静态文件
│   ├── index.html        # 主页
│   ├── history.html      # 历史记录
│   ├── 3d-viewer.html    # 3D模型查看器
│   ├── damage-viewer.html # 3D损伤可视化
│   ├── css/style.css     # 样式文件
│   ├── js/main.js        # 前端逻辑
│   ├── images/           # 图片资源（logo等）
│   └── upload/           # 上传文件目录
│
├── utils/                # 工具类
│   ├── logger.py         # 日志管理
│   ── response.py       # 统一响应格式
│
├── data/                 # 数据目录
│   └── sensor.db         # SQLite数据库
│
├── logs/                 # 日志文件
└── runs/                 # YOLO训练结果（已忽略）
```

## 🔧 配置说明

编辑 `.env` 文件进行配置：

```env
# 服务器配置
HOST=0.0.0.0
PORT=8000

# YOLO模型配置
YOLO_MODEL_PATH=runs/car_damage_yolov8n/weights/best.pt
YOLO_CONF_THRESHOLD=0.15

# LLM配置（用于生成报告）
LM_STUDIO_URL=http://localhost:1234/v1
ENABLE_LLM_REPORT=true
LLM_MAX_TOKENS=4096
```

## 📡 API接口

### 核心接口

- `POST /api/v1/sensor/upload` - 上传图片并检测
- `GET /api/v1/sensor/history` - 获取历史记录
- `GET /api/v1/sensor/{id}` - 获取单条记录详情
- `DELETE /api/v1/sensor/{id}` - 删除记录

### 示例请求

```bash
# 上传图片检测
curl -X POST http://localhost:8000/api/v1/sensor/upload \
  -F "file=@car_image.jpg" \
  -F "vehicle_type=sedan"

# 获取历史记录
curl http://localhost:8000/api/v1/sensor/history
```

## 🛠️ 技术栈

- **后端**：FastAPI + Python 3.9+
- **AI模型**：YOLOv8（Ultralytics）
- **LLM**：Qwen 2.5（通过LM Studio）
- **数据库**：SQLite
- **前端**：HTML5 + CSS3 + JavaScript
- **3D渲染**：Three.js + GLTF模型

##  注意事项

1. **首次启动**会自动初始化数据库和目录结构
2. **模型文件**：需要下载YOLO预训练模型到项目根目录
3. **LLM服务**：如需生成智能报告，需启动LM Studio服务
4. **文件上传**：默认限制10MB，支持JPG/PNG/GIF/BMP格式

## 🐳 Docker部署（可选）

```bash
# 构建镜像
docker build -t smartinspect-vision .

# 运行容器
docker run -p 8000:8000 -v ./data:/app/data smartinspect-vision
```

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交Issue和Pull Request！

---

**智检慧眼** - 让车辆检测更智能、更高效 🚀
