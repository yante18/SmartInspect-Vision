#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一 API 响应格式工具
"""
from typing import Any, Optional, Dict, List
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import json

class ApiResponse(BaseModel):
    """统一 API 响应格式"""
    code: int = Field(..., description="响应状态码，0表示成功，其他表示失败")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(default=None, description="响应数据")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "操作成功",
                "data": {},
                "timestamp": "2024-01-01T12:00:00"
            }
        }

def success_response(data: Any = None, message: str = "操作成功") -> JSONResponse:
    """
    成功响应
    
    :param data: 响应数据
    :param message: 成功消息
    :return: JSONResponse
    """
    response = ApiResponse(code=0, message=message, data=data)
    return JSONResponse(
        content=response.model_dump(),
        status_code=200
    )

def error_response(code: int, message: str = "操作失败", data: Any = None) -> JSONResponse:
    """
    错误响应
    
    :param code: 错误码（建议大于0）
    :param message: 错误消息
    :param data: 附加数据
    :return: JSONResponse
    """
    response = ApiResponse(code=code, message=message, data=data)
    return JSONResponse(
        content=response.model_dump(),
        status_code=200  # 使用 200，让前端通过 code 判断错误
    )

def validation_error_response(errors: List[Dict], message: str = "参数验证失败") -> JSONResponse:
    """
    参数验证失败响应
    
    :param errors: 验证错误列表
    :param message: 错误消息
    :return: JSONResponse
    """
    return error_response(code=400, message=message, data={"errors": errors})

def not_found_response(message: str = "资源不存在") -> JSONResponse:
    """
    资源不存在响应
    
    :param message: 错误消息
    :return: JSONResponse
    """
    return error_response(code=404, message=message)

def unauthorized_response(message: str = "未授权访问") -> JSONResponse:
    """
    未授权响应
    
    :param message: 错误消息
    :return: JSONResponse
    """
    return error_response(code=401, message=message)

def server_error_response(message: str = "服务器内部错误") -> JSONResponse:
    """
    服务器错误响应
    
    :param message: 错误消息
    :return: JSONResponse
    """
    return error_response(code=500, message=message)


# 常用错误码
class ErrorCode:
    SUCCESS = 0
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500
    # 业务错误码
    MODEL_NOT_LOADED = 1001
    INVALID_IMAGE = 1002
    DETECTION_FAILED = 1003
    UPLOAD_FAILED = 1004
