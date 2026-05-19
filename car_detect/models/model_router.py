from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import Optional
import uuid
import shutil
from datetime import datetime
from pathlib import Path

from config import settings
from utils.logger import log
from utils.validator import validator
from models.yolo_detect import run_yolo_detection
from models.qwen_report import generate_inspection_report
from models.database import get_db, DetectionRecord
from sensor.sensor_api import DetectionResult

router = APIRouter()

@router.post("/detect", response_model=DetectionResult)
async def detect_vehicle(
    file: UploadFile = File(...),
    vehicle_type: Optional[str] = Form("sedan")
):
    """
    车辆检测接口（车主自检）
    :param file: 上传的车辆图片
    :param vehicle_type: 车辆类型
    :return: 检测结果和报告
    """
    try:
        # 校验文件
        file_info = validator.validate_image_file(file)
        
        # 生成唯一文件名并保存
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = settings.UPLOAD_DIR / unique_filename
        
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        log.info(f"开始检测: {unique_filename}")
        
        # 执行YOLO检测
        detection_result = run_yolo_detection(str(upload_path))
        
        # 生成检测报告
        report = generate_inspection_report(
            detection_data={
                "upload_time": datetime.now().isoformat(),
                "detection_count": detection_result.detection_count
            },
            vehicle_type=vehicle_type
        )
        
        log.info(f"检测完成: {unique_filename}, 检测到 {detection_result.detection_count} 个对象")
        
        # 保存检测记录到数据库
        db = next(get_db())
        try:
            record = DetectionRecord(
                filename=unique_filename,
                original_name=file.filename,
                vehicle_type=vehicle_type,
                detection_count=detection_result.detection_count,
                confidence_score=0.0,  # 可以在YOLO检测中获取
                report_content=report
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            log.info(f"检测记录已保存，ID: {record.id}")
        except Exception as e:
            db.rollback()
            log.error(f"保存检测记录失败: {str(e)}")
        finally:
            db.close()
        
        return DetectionResult(
            code=0,
            msg="检测成功",
            data={
                "filename": unique_filename,
                "detections": detection_result.dict(),
                "report": report,
                "processing_time": datetime.now().isoformat()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"检测失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")

@router.post("/damage-assessment", response_model=DetectionResult)
async def damage_assessment(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    快速定损接口（预留）
    :param file: 损伤部位图片
    :param description: 损伤描述
    :return: 定损结果
    """
    # TODO: 实现定损规则引擎
    return DetectionResult(
        code=0,
        msg="定损功能开发中",
        data={"status": "pending"}
    )

@router.post("/patrol", response_model=DetectionResult)
async def patrol_inspection(
    files: list[UploadFile] = File(...),
    route_id: Optional[str] = Form(None)
):
    """
    社区巡检接口（预留，支持批量上传）
    :param files: 多张图片
    :param route_id: 巡检路线ID
    :return: 巡检结果
    """
    # TODO: 实现批量处理和路线标记
    return DetectionResult(
        code=0,
        msg="巡检功能开发中",
        data={"status": "pending", "file_count": len(files)}
    )

@router.get("/history")
async def get_history(
    page: int = 1,
    page_size: int = 10,
    db=Depends(get_db)
):
    """
    获取检测历史记录
    :param page: 页码（从1开始）
    :param page_size: 每页数量
    :return: 历史记录列表
    """
    try:
        # 计算总数
        total = db.query(DetectionRecord).count()
        
        # 分页查询，按时间倒序
        records = db.query(DetectionRecord).order_by(
            DetectionRecord.created_at.desc()
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        # 转换为字典列表
        records_list = []
        for record in records:
            records_list.append({
                "id": record.id,
                "filename": record.filename,
                "original_name": record.original_name,
                "vehicle_type": record.vehicle_type,
                "detection_count": record.detection_count,
                "confidence_score": record.confidence_score,
                "report": record.report_content,
                "created_at": record.created_at.isoformat()
            })
        
        return {
            "code": 0,
            "msg": "查询成功",
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "records": records_list
            }
        }
    except Exception as e:
        log.error(f"查询历史记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.delete("/history/{record_id}")
async def delete_history_record(
    record_id: int,
    db=Depends(get_db)
):
    """
    删除检测记录
    :param record_id: 记录ID
    :return: 删除结果
    """
    try:
        record = db.query(DetectionRecord).filter(DetectionRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="记录不存在")
        
        # 删除记录
        db.delete(record)
        db.commit()
        
        # 删除对应的图片文件
        upload_path = settings.UPLOAD_DIR / record.filename
        if upload_path.exists():
            upload_path.unlink()
        
        return {
            "code": 0,
            "msg": "删除成功",
            "data": None
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        log.error(f"删除记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
