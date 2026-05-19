from loguru import logger
import sys
from pathlib import Path
from config import settings

def setup_logger():
    """配置日志系统"""
    # 移除默认handler
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # 文件输出（按天切割）
    log_file = settings.LOG_DIR / "app_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_file),
        level=settings.LOG_LEVEL,
        rotation="00:00",
        retention="30 days",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    return logger

# 创建全局logger实例
log = setup_logger()
