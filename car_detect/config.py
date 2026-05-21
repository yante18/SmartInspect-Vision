from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """全局配置管理"""
    
    # 项目基础配置
    PROJECT_NAME: str = "智检慧眼"
    API_PREFIX: str = "/api/v1"
    VERSION: str = "1.0.0"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 文件路径配置
    BASE_DIR: Path = Path(__file__).parent
    UPLOAD_DIR: Path = Path(__file__).parent / "static" / "upload"
    DB_PATH: Path = Path(__file__).parent / "data" / "sensor.db"
    LOG_DIR: Path = Path(__file__).parent / "logs"
    
    # 文件上传限制
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "bmp"}
    ALLOWED_MIME_TYPES: set = {"image/jpeg", "image/png", "image/gif", "image/bmp"}
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 远程 YOLO 服务配置（分布式架构）
    REMOTE_YOLO_URL: str = "http://localhost:9000"  # 本地服务地址
    YOLO_API_TOKEN: str = "your-secret-token-here"  # API 认证 Token
    USE_REMOTE_YOLO: bool = False  # 是否使用远程服务（False=本地推理，True=远程调用）
    REMOTE_YOLO_TIMEOUT: int = 30  # 请求超时时间（秒）
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 创建全局配置实例
settings = Settings()

# 确保必要目录存在
def init_directories():
    """初始化必要的目录结构"""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
