# 智检慧眼 - 车辆智能检测系统 

AI驱动的车辆损伤智能检测系统，基于YOLOv8和LLM技术，提供车主自检、快速定损、社区巡检功能。

## ✨ 主要特性

- 🤖 **AI损伤检测**：基于YOLOv8的34类车辆损伤自动识别（置信度≥15%）
-  **智能报告生成**：使用Qwen LLM生成专业的检测报告
-  **3D模型展示**：支持小米SU7 Max车型的3D可视化查看
-  **3D损伤标记**：在3D模型上精准标注损伤位置和类型
-  **Web界面**：响应式设计，支持PC和移动端访问
- 🔌 **RESTful API**：完整的API接口支持第三方集成
-  **历史记录**：自动保存所有检测记录到SQLite数据库
- 📈 **Canvas叠加层**：检测结果图片上实时绘制损伤框

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

2. **启动项目**

**Windows快捷启动：**
```bash
# 方式1：使用启动脚本（推荐）
cd SmartInspect-Vision/car_detect
start.bat

# 方式2：手动启动
python main.py
```

**Linux/Mac启动：**
```bash
cd SmartInspect-Vision/car_detect
chmod +x deploy.sh
./deploy.sh

# 或手动启动
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
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
│   ├── database.py       # SQLite数据库模型
│   ├── model_router.py   # YOLO检测路由（核心）
│   ├── qwen_report.py    # LLM报告生成
│   ├── yolo_engine.py    # YOLO推理引擎
│   └── remote_yolo_client.py  # 远程YOLO客户端（分布式）
│
├── sensor/               # 传感器API
│   └── sensor_api.py     # 检测记录管理
│
├── static/               # 前端静态文件
│   ├── index.html        # 主页（车辆检测）
│   ├── history.html      # 历史记录页
│   ├── 3d-viewer.html    # 3D模型查看器（小米SU7）
│   ├── damage-viewer.html # 3D损伤可视化
│   ├── css/style.css     # 样式文件
│   ├── js/
│   │   ├── config.js     # 全局配置（API_BASE等）
│   │   ├── api.js        # API请求封装
│   │   ├── icons.js      # SVG图标库
│   │   ├── utils.js      # 工具函数
│   │   ── main.js       # 主逻辑（已废弃，保留兼容）
│   ├── images/logo.png   # Logo图片
│   ├── 2024_xiaomi_su7_max/  # 小米SU7 3D模型资源
│   │   ├── scene.gltf    # GLTF模型文件
│   │   ├── scene.bin     # 二进制数据
│   │   └── textures/     # 26个纹理贴图
│   ── upload/           # 上传文件目录（.gitignore）
│
├── utils/                # 工具类
│   ├── logger.py         # 日志管理系统
│   ├── response.py       # 统一响应格式
│   ── validator.py      # 文件校验工具
│
├── data/                 # 数据目录
│   └── sensor.db         # SQLite数据库（.gitignore）
│
├── logs/                 # 运行日志（.gitignore）
├── runs/                 # YOLO训练结果（.gitignore）
├── venv/                 # Python虚拟环境（.gitignore）
── .env.example          # 环境变量示例
── Dockerfile            # Docker镜像构建
── docker-compose.yml    # Docker编排
└── requirements.txt      # Python依赖包
