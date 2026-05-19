from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import traceback

from config import settings, init_directories
from utils.logger import log
from models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    log.info("🚀 智检慧眼系统启动中...")
    
    # 初始化目录
    init_directories()
    log.info(f"✅ 目录初始化完成")
    
    # 初始化数据库
    init_db()
    log.info(f"✅ 数据库初始化完成: {settings.DB_PATH}")
    
    log.info(f"✅ 系统启动成功！监听地址: http://{settings.HOST}:{settings.PORT}")
    
    yield
    
    # 关闭时清理
    log.info("👋 系统关闭中...")

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI驱动的车辆智能检测系统",
    lifespan=lifespan
)

# 添加CORS中间件（支持跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由模块
from sensor.sensor_api import router as sensor_router
from models.model_router import router as model_router

app.include_router(sensor_router, prefix=f"{settings.API_PREFIX}/sensor", tags=["传感器接口"])
app.include_router(model_router, prefix=f"{settings.API_PREFIX}/models", tags=["模型检测接口"])

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """统一异常处理"""
    error_trace = traceback.format_exc()
    log.error(f"未处理的异常: {error_trace}")
    
    return JSONResponse(
        status_code=500,
        content={
            "code": -1,
            "msg": "服务器内部错误",
            "data": None
        }
    )

# 根路径
@app.get("/", response_class=HTMLResponse)
async def root():
    """返回主页"""
    try:
        with open("static/index.html", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"code": -1, "msg": "页面不存在", "data": None}
        )

# 历史记录页面
@app.get("/history.html", response_class=HTMLResponse)
async def history():
    """返回历史记录页面"""
    try:
        with open("static/history.html", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"code": -1, "msg": "页面不存在", "data": None}
        )

# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # 开发模式自动重载
        log_level=settings.LOG_LEVEL.lower()
    )
