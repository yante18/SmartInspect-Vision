# 📘 智检慧眼｜车辆智能检测系统开发文档（FastAPI预留接口版）

> 本文档基于模块化架构设计，提供从零到一的完整落地方案。核心面向**车主自检、快速定损、社区巡检**三大场景，并预留标准化扩展接口，便于后续无缝接入用户系统、小程序与数据统计模块。

---
## 📦 一、项目目录结构（精确到文件）
```plaintext
car_detect/
├── main.py               # FastAPI主程序（含全局异常处理、路由注册、静态文件挂载）
├── config.py             # 全局配置（集中管理所有参数，支持环境变量覆盖）
├── requirements.txt      # Python依赖清单
├── .gitignore            # Git忽略规则（可选）
├── README.md             # 项目说明与快速启动指南
├── static/               # 前端静态资源
│   ├── index.html        # 主检测页面
│   ├── history.html      # 历史记录查询页
│   ├── css/style.css     # 全局样式
│   ├── js/main.js        # 核心交互逻辑（请求封装、DOM渲染）
│   └── upload/           # 临时上传目录（自动创建）
├── sensor/               # 传感器与数据校验层
│   ├── __init__.py
│   └── sensor_api.py     # 图像/视频流接口（含格式、大小、字段校验）
├── models/               # AI推理与报告生成层
│   ├── __init__.py
│   ├── yolo_detect.py    # YOLOv8/v5目标检测接口（预留模型加载逻辑）
│   └── qwen_report.py    # 大语言模型报告生成接口（预留Prompt模板）
├── utils/                # 公共工具集
│   ├── __init__.py
│   ├── logger.py         # 结构化日志（按天切割+分级输出）
│   └── validator.py      # 通用数据校验器（MIME、尺寸、JSON Schema）
├── data/                 # 持久化存储
│   └── sensor.db         # SQLite数据库（自动建表）
└── logs/                 # 运行日志
    └── app.log
```

---
## 🛠️ 二、环境配置与依赖安装
### 2.1 Python 版本要求
- `Python >= 3.9`
- 建议使用虚拟环境：`python -m venv venv && source venv/bin/activate`（Linux/macOS）或 `venv\Scripts\activate`（Windows）

### 2.2 依赖清单 (`requirements.txt`)
```text
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.5.0
aiofiles>=23.2.1
sqlalchemy>=2.0.23
python-dotenv>=1.0.0
loguru>=0.7.2
# AI推理预留（按需安装）
# ultralytics>=8.0.0
# dashscope>=1.10.0  # 阿里云通义千问SDK
```

---
## ⚙️ 三、核心模块实现要点

### 3.1 配置管理 (`config.py`)
```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "智检慧眼"
    API_PREFIX: str = "/api/v1"
    UPLOAD_DIR: Path = Path(__file__).parent / "static/upload"
    DB_PATH: Path = Path(__file__).parent / "data/sensor.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 3.2 主程序入口 (`main.py`)
```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化目录、日志、数据库表结构
    yield
    # 关闭时清理资源（如模型卸载）

app = FastAPI(title="智检慧眼 API", version="1.0.0", lifespan=lifespan)

# 挂载静态文件（解决前端资源404）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由模块
from sensor import router as sensor_router
from models import router as model_router

app.include_router(sensor_router, prefix="/api/v1/sensor", tags=["sensor"])
app.include_router(model_router, prefix="/api/v1/models", tags=["models"])

# 全局异常处理（统一返回格式）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(f"Unhandled error: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"code": -1, "msg": "服务器内部错误", "data": None}
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()
```

### 3.3 预留扩展接口设计（核心）
为支撑**用户系统、小程序、数据统计**，所有业务路由统一遵循以下契约：
| 场景 | 预留路径 | 状态 | 说明 |
|------|----------|------|------|
| 车主自检 | `/api/v1/inspect/self` | ✅ 已实现 | 基础图像上传+YOLO推理 |
| 快速定损 | `/api/v1/inspect/damage` | 🔌 预留 | 需对接定损规则引擎 |
| 社区巡检 | `/api/v1/inspect/patrol` | 🔌 预留 | 支持批量上传与路线标记 |
| 用户授权 | `/api/v1/auth/login` | 🔌 预留 | JWT鉴权，后续接小程序OpenID |
| 数据统计 | `/api/v1/stats/dashboard` | 🔌 预留 | 聚合上报量、缺陷分布、趋势图表 |

> 💡 **扩展规范**：新增模块只需在 `main.py` 中注册新 Router，并在对应文件内实现业务逻辑即可快速上线。

---
## 🌐 四、前端交互与请求封装 (`static/js/main.js`)
```javascript
const API_BASE = '/api/v1';

async function submitDetection(formId) {
    const btn = document.getElementById('submitBtn');
    const resultDiv = document.getElementById('result');
    
    try {
        btn.disabled = true;
        btn.textContent = '检测中...';
        
        const formData = new FormData(document.getElementById(formId));
        const res = await fetch(`${API_BASE}/models/detect`, { method: 'POST', body: formData });
        const data = await res.json();

        if (data.code === 0) {
            resultDiv.innerHTML = `<p style="color:#2e7d32">✅ ${data.msg}</p>`;
        } else {
            throw new Error(data.msg || '检测异常');
        }
    } catch (err) {
        resultDiv.innerHTML = `<p style="color:red">❌ ${err.message || '网络错误，请检查服务是否启动'}</p>`;
    } finally {
        btn.disabled = false;
        btn.textContent = '提交检测';
    }
}
```

---
## 🔍 五、常见问题排查（重点：URL拼写报错）
> 📌 **现象**：浏览器访问 `http://127.0.0.1:8000/` 提示 *“URL拼写可能存在错误，请检查”* 或返回空白页。

### ✅ 标准排查清单
| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1️⃣ 端口占用 | `lsof -i :8000`（Linux）或 `netstat -ano \| findstr :8000`（Win） | 确认未被其他进程抢占 |
| 2️⃣ 启动命令 | 必须使用 `uvicorn main:app --host 127.0.0.1 --port 8000 --reload` | `--reload` 便于热更新，不写 `main.py` 仅写 `main` 会报模块错误 |
| 3️⃣ 路由前缀 | FastAPI 默认根路径为 `/`，若访问 `/index.html` 需显式挂载或重定向 | 修改 `main.py` 中 `@app.get("/index.html")` 或直接访问 `/` |
| 4️⃣ CORS跨域 | 前端独立部署时需添加 `CORSMiddleware` | `from fastapi.middleware.cors import CORSMiddleware; app.add_middleware(...)` |
| 5️⃣ 静态文件路径 | `static/upload/` 必须存在，否则启动报错 | 在 `lifespan` 中调用 `settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)` |

---
## 🚀 六、部署与交付方案
### 6.1 本地运行
```bash
pip install -r requirements.txt
python main.py   # 默认监听 http://127.0.0.1:8000
```

### 6.2 云服务器一键部署（推荐）
- **环境**：Ubuntu 22.04 / CentOS Stream 9 / Debian 12
- **方案**：`Nginx(反代) + Uvicorn(Systemd) + SQLite`
- **优势**：支持 HTTPS、静态资源缓存、自动重启、日志轮转

### 6.3 交付选项（按需选择）
| 交付形式 | 适用场景 | 包含内容 |
|----------|----------|----------|
| 📦 压缩包打包 | 本地调试/内网部署 | 完整源码 + `.env.example` + `deploy.sh` 启动脚本 |
| ☁️ 云服务器部署 | 生产环境/对外服务 | SSH 权限移交 + 域名绑定 + HTTPS证书配置 |

---
## 🔮 七、后续扩展路线
1. **用户系统**：接入 JWT/OAuth2，增加 `/auth/register`、`/user/profile`
2. **小程序端**：复用现有 API，替换 `main.js` 为 `uni.request` + 云开发存储
3. **数据统计看板**：定时任务聚合 SQLite 数据，输出 ECharts 兼容 JSON 至 `/stats/dashboard`
4. **模型升级**：热加载 YOLO/Qwen 权重文件，支持 `hot-reload` 无需重启服务

---
> 📝 **注**：本文档部分架构设计与代码示例由 AI 辅助生成并经过人工校验。如需完整可运行压缩包或免费云服务器部署支持，请回复具体交付形式，我将直接输出对应环境包与执行脚本。