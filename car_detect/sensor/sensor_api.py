from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from pydantic import BaseModel
import uuid
import shutil
from pathlib import Path
from datetime import datetime

from config import settings
from utils.logger import log
from utils.validator import validator

router = APIRouter()

class DetectionResult(BaseModel):
    """检测结果响应模型"""
    code: int
    msg: str
    data: Optional[dict] = None

@router.post("/upload", response_model=DetectionResult)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    上传车辆图片接口
    :param file: 上传的图片文件
    :param description: 图片描述（可选）
    :return: 上传结果
    """
    try:
        # 校验文件
        file_info = validator.validate_image_file(file)
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = settings.UPLOAD_DIR / unique_filename
        
        # 保存文件
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        log.info(f"文件上传成功: {unique_filename}, 大小: {file_info['size']} bytes")
        
        return DetectionResult(
            code=0,
            msg="上传成功",
            data={
                "filename": unique_filename,
                "original_name": file.filename,
                "size": file_info["size"],
                "upload_time": datetime.now().isoformat(),
                "description": description
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"文件上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.get("/info")
async def get_sensor_info():
    """获取传感器信息接口（预留）"""
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "supported_formats": list(settings.ALLOWED_EXTENSIONS),
            "max_file_size_mb": settings.MAX_FILE_SIZE / 1024 / 1024,
            "upload_dir": str(settings.UPLOAD_DIR)
        }
    }
