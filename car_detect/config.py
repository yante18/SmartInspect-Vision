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
    
    # YOLO 模型配置
    YOLO_MODEL_PATH: str = "runs/car_damage_yolov8n/weights/best.pt"  # 使用训练好的模型
    YOLO_FALLBACK_PATH: str = "yolov8n.pt"  # 备用预训练模型
    YOLO_CONF_THRESHOLD: float = 0.15  # 置信度阈值（降低以检测到更多损伤）
    YOLO_IOU_THRESHOLD: float = 0.45  # NMS IOU 阈值
    
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
    
    # LM Studio LLM 配置（用于生成智能报告）
    LM_STUDIO_URL: str = "http://localhost:1234/v1"  # LM Studio API 地址
    LM_STUDIO_MODEL: str = "qwen2.5-7b-instruct"  # 使用的模型名称
    LM_STUDIO_API_TOKEN: str = ""  # LM Studio API Token（如果启用了认证）
    ENABLE_LLM_REPORT: bool = True  # 是否启用 LLM 生成报告
    LLM_TIMEOUT: int = 60  # LLM 请求超时时间（秒）
    LLM_TEMPERATURE: float = 0.7  # 生成温度（0-1，越高越随机）
    LLM_MAX_TOKENS: int = 4096  # 最大生成 token 数（增加到 4096 以支持完整报告）
    
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
