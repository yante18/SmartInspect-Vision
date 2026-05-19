# 📁 项目完整结构

```
car_detect/                              # 项目根目录
│
├── 📄 main.py                           # FastAPI主程序入口
├── 📄 config.py                         # 全局配置管理
├── 📄 requirements.txt                  # Python依赖清单
├── 📄 .env.example                      # 环境配置示例
├── 📄 .gitignore                        # Git忽略规则
│
├── 🚀 deploy.sh                         # Linux一键部署脚本
├── 🚀 start.bat                         # Windows启动脚本
├── 🚀 package.sh                        # 项目打包脚本
│
├── 📖 README.md                         # 完整项目文档
├── 📖 QUICKSTART.md                     # 快速开始指南
├── 📖 DELIVERY.md                       # 项目交付清单
├── 📖 program.markdown                  # 原始需求文档
├── 📖 nginx.conf.example                # Nginx配置示例
│
├── 📂 sensor/                           # 传感器模块
│   ├── __init__.py
│   └── sensor_api.py                    # 图像上传接口
│
├── 📂 models/                           # AI模型模块
│   ├── __init__.py
│   ├── yolo_detect.py                   # YOLO检测（预留）
│   ├── qwen_report.py                   # 报告生成（预留）
│   ├── model_router.py                  # 模型路由
│   └── database.py                      # 数据库模型
│
├── 📂 utils/                            # 工具模块
│   ├── __init__.py
│   ├── logger.py                        # 日志系统
│   └── validator.py                     # 数据校验器
│
├── 📂 static/                           # 前端静态资源
│   ├── index.html                       # 主检测页面
│   ├── history.html                     # 历史记录页
│   │
│   ├── 📂 css/
│   │   └── style.css                    # 全局样式
│   │
│   ├── 📂 js/
│   │   └── main.js                      # 核心交互逻辑
│   │
│   └── 📂 upload/                       # 上传文件目录
│       └── .gitkeep
│
├── 📂 data/                             # 数据存储（运行时创建）
│   └── sensor.db                        # SQLite数据库
│
└── 📂 logs/                             # 运行日志（运行时创建）
    └── app_YYYY-MM-DD.log               # 按天切割的日志文件
```

## 📊 文件统计

### 核心代码文件
- **Python后端**: 11个文件
  - main.py (主程序)
  - config.py (配置)
  - sensor/sensor_api.py (上传接口)
  - models/yolo_detect.py (YOLO检测)
  - models/qwen_report.py (报告生成)
  - models/model_router.py (模型路由)
  - models/database.py (数据库)
  - models/__init__.py
  - utils/logger.py (日志)
  - utils/validator.py (校验)
  - utils/__init__.py

- **前端页面**: 4个文件
  - static/index.html (主页)
  - static/history.html (历史)
  - static/css/style.css (样式)
  - static/js/main.js (交互)

### 配置文件
- .env.example (环境配置)
- .gitignore (Git规则)
- requirements.txt (依赖)
- nginx.conf.example (Nginx)

### 部署脚本
- deploy.sh (Linux部署)
- start.bat (Windows启动)
- package.sh (项目打包)

### 文档文件
- README.md (完整文档)
- QUICKSTART.md (快速开始)
- DELIVERY.md (交付清单)
- program.markdown (需求文档)

**总计**: 25个核心文件 + 运行时生成的目录

---

## 🎯 关键文件说明

### 后端核心
| 文件 | 作用 | 行数 |
|------|------|------|
| main.py | FastAPI应用入口，路由注册 | ~110行 |
| config.py | 配置管理，支持环境变量 | ~45行 |
| sensor_api.py | 图片上传与校验 | ~76行 |
| model_router.py | 检测业务逻辑 | ~107行 |
| database.py | 数据库模型定义 | ~40行 |

### 前端核心
| 文件 | 作用 | 行数 |
|------|------|------|
| index.html | 主页面结构 | ~70行 |
| style.css | 响应式样式 | ~272行 |
| main.js | 交互逻辑 | ~218行 |

### 工具模块
| 文件 | 作用 | 行数 |
|------|------|------|
| logger.py | 日志系统配置 | ~34行 |
| validator.py | 数据校验器 | ~69行 |

---

## 🔗 模块依赖关系

```
main.py (主程序)
  ├─→ config.py (配置)
  ├─→ utils/logger.py (日志)
  ├─→ models/database.py (数据库)
  ├─→ sensor/sensor_api.py (传感器路由)
  └─→ models/model_router.py (模型路由)
       ├─→ utils/validator.py (校验)
       ├─→ models/yolo_detect.py (YOLO)
       └─→ models/qwen_report.py (报告)

static/index.html (前端)
  ├─→ static/css/style.css (样式)
  └─→ static/js/main.js (交互)
       └─→ /api/v1/models/detect (后端API)
```

---

## 📦 运行时生成的文件

首次运行后会自动创建：
- `data/sensor.db` - SQLite数据库文件
- `logs/app_YYYY-MM-DD.log` - 日志文件
- `static/upload/*` - 上传的图片文件
- `venv/` - Python虚拟环境（如果执行了安装脚本）

---

**项目结构清晰，模块化设计，易于维护和扩展！** ✨
