"""
本地 YOLO 推理服务
在本地电脑运行，暴露 HTTP 接口供云服务器调用
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import uuid
import tempfile
import os
from pathlib import Path

# 导入 YOLO 引擎
import sys
sys.path.insert(0, str(Path(__file__).parent))
from models.yolo_engine import get_detector

app = FastAPI(title="Local YOLO Inference Service", version="1.0.0")

# CORS 配置（允许云服务器访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为云服务器IP
    allow_methods=["*"],
    allow_headers=["*"],
)

# 认证 Token（简单安全机制）
API_TOKEN = os.getenv("YOLO_API_TOKEN", "your-secret-token-here")

def verify_token(token: str = Header(None)):
    """验证 API Token"""
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

class DetectionResponse(BaseModel):
    """检测结果响应模型"""
    code: int
    msg: str
    data: Optional[Dict] = None

@app.get("/health")
async def health_check():
    """健康检查接口"""
    detector = get_detector()
    return {
        "status": "ok",
        "detector_loaded": detector.is_deployed,
        "model_name": detector.model_name
    }

@app.post("/detect", response_model=DetectionResponse)
async def detect_vehicle(
    file: UploadFile = File(...),
    x_api_token: str = Header(None)
):
    """
    车辆检测接口
    :param file: 上传的车辆图片
    :param x_api_token: API 认证 Token
    :return: 检测结果
    """
    # 验证 Token
    verify_token(x_api_token)
    
    try:
        # 保存临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # 执行 YOLO 检测
            detector = get_detector()
            results = detector.detect(tmp_path)
            
            return DetectionResponse(
                code=0,
                msg="检测成功",
                data={
                    "detection_count": len(results),
                    "results": results
                }
            )
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@app.post("/detect_and_draw", response_model=DetectionResponse)
async def detect_and_draw(
    file: UploadFile = File(...),
    x_api_token: str = Header(None)
):
    """
    检测并绘制结果图
    :param file: 上传的图片
    :param x_api_token: API 认证 Token
    :return: 检测结果和标注图片
    """
    verify_token(x_api_token)
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            detector = get_detector()
            
            # 执行检测
            results = detector.detect(tmp_path)
            
            # 绘制结果
            output_path = tmp_path.replace(".jpg", "_result.jpg")
            detector.detect_and_draw(tmp_path, output_path)
            
            # 读取结果图片
            with open(output_path, "rb") as f:
                result_image = f.read()
            
            import base64
            encoded_image = base64.b64encode(result_image).decode('utf-8')
            
            return DetectionResponse(
                code=0,
                msg="检测并绘制成功",
                data={
                    "detection_count": len(results),
                    "results": results,
                    "annotated_image_base64": encoded_image
                }
            )
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            output_path = tmp_path.replace(".jpg", "_result.jpg")
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动本地 YOLO 推理服务")
    print("=" * 60)
    print(f"📍 服务地址: http://0.0.0.0:9000")
    print(f"🔑 API Token: {API_TOKEN}")
    print(f"📖 API 文档: http://localhost:9000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        log_level="info"
    )
