from typing import Optional
from fastapi import UploadFile, HTTPException
from config import settings
import os

class DataValidator:
    """通用数据校验器"""
    
    @staticmethod
    def validate_image_file(file: UploadFile) -> dict:
        """
        校验上传的图片文件
        :param file: 上传的文件对象
        :return: 文件信息字典
        """
        # 检查文件名
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 检查文件扩展名
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式: {ext}。支持的格式: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # 读取文件内容进行MIME类型校验
        content = file.file.read()
        file_size = len(content)
        
        # 检查文件大小
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB)"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="文件内容为空")
        
        # 重置文件指针
        file.file.seek(0)
        
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size,
            "extension": ext
        }
    
    @staticmethod
    def validate_json_data(data: dict, required_fields: list) -> None:
        """
        校验JSON数据的必需字段
        :param data: 待校验的字典数据
        :param required_fields: 必需字段列表
        """
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"缺少必需字段: {', '.join(missing_fields)}"
            )

# 创建全局校验器实例
validator = DataValidator()
