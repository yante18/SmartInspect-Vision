from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import Optional
import uuid
import shutil
from datetime import datetime
from pathlib import Path

from config import settings
from utils.logger import log
from utils.validator import validator

# 根据配置选择本地或远程 YOLO
if settings.USE_REMOTE_YOLO:
    from models.remote_yolo_client import get_remote_client as get_detector
    log.info("[ModelRouter] 使用远程 YOLO 服务")
else:
    from models.yolo_engine import get_detector
    log.info("[ModelRouter] 使用本地 YOLO 模型")

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
        detector = get_detector()
        yolo_results = detector.detect(str(upload_path))
        
        # 绘制检测结果（可选）
        # result_img_path = detector.detect_and_draw(str(upload_path))
        
        # 生成检测报告
        report = generate_inspection_report(
            detection_data={
                "upload_time": datetime.now().isoformat(),
                "detection_count": len(yolo_results),
                "detections": yolo_results
            },
            vehicle_type=vehicle_type
        )
        
        log.info(f"检测完成: {unique_filename}, 检测到 {len(yolo_results)} 个对象")
        
        # 保存检测记录到数据库
        db = next(get_db())
        try:
            # 计算平均置信度
            avg_conf = sum(d['confidence'] for d in yolo_results) / len(yolo_results) if yolo_results else 0.0
            
            record = DetectionRecord(
                filename=unique_filename,
                original_name=file.filename,
                vehicle_type=vehicle_type,
                detection_count=len(yolo_results),
                confidence_score=avg_conf,
                report_content=report,
                detections=yolo_results  # 新增：保存完整的检测结果
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
                "detections": {
                    "detection_count": len(yolo_results),
                    "results": yolo_results
                },
                "report": report,
                "processing_time": datetime.now().isoformat(),
                "image_url": f"/static/upload/{unique_filename}"
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
    快速定损接口
    :param file: 损伤部位图片
    :param description: 损伤描述
    :return: 定损结果
    """
    try:
        # 校验文件
        file_info = validator.validate_image_file(file)
        
        # 生成唯一文件名并保存
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        upload_path = settings.UPLOAD_DIR / unique_filename
        
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        log.info(f"开始定损评估: {unique_filename}")
        
        # 执行YOLO检测
        detector = get_detector()
        yolo_results = detector.detect(str(upload_path))
        
        # 基于检测结果进行定损评估
        assessment = perform_damage_assessment(yolo_results, description)
        
        log.info(f"定损完成: {unique_filename}, 评估等级: {assessment['severity_level']}")
        
        return DetectionResult(
            code=0,
            msg="定损评估完成",
            data={
                "filename": unique_filename,
                "detections": yolo_results,
                "assessment": assessment,
                "processing_time": datetime.now().isoformat(),
                "image_url": f"/static/upload/{unique_filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"定损失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"定损失败: {str(e)}")

@router.post("/patrol", response_model=DetectionResult)
async def patrol_inspection(
    files: list[UploadFile] = File(...),
    route_id: Optional[str] = Form(None)
):
    """
    社区巡检接口（支持批量上传）
    :param files: 多张图片
    :param route_id: 巡检路线ID
    :return: 巡检结果
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="请至少上传一张图片")
        
        log.info(f"开始批量巡检: {len(files)} 张图片, 路线ID: {route_id}")
        
        detector = get_detector()
        patrol_results = []
        total_detections = 0
        
        for i, file in enumerate(files, 1):
            try:
                # 校验文件
                file_info = validator.validate_image_file(file)
                
                # 生成唯一文件名并保存
                unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
                upload_path = settings.UPLOAD_DIR / unique_filename
                
                with upload_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # 执行检测
                yolo_results = detector.detect(str(upload_path))
                total_detections += len(yolo_results)
                
                patrol_results.append({
                    "index": i,
                    "filename": unique_filename,
                    "original_name": file.filename,
                    "detection_count": len(yolo_results),
                    "detections": yolo_results,
                    "image_url": f"/static/upload/{unique_filename}"
                })
                
                log.info(f"处理进度: {i}/{len(files)}, 检测到 {len(yolo_results)} 个对象")
                
            except Exception as e:
                log.error(f"处理第 {i} 张图片失败: {str(e)}")
                patrol_results.append({
                    "index": i,
                    "filename": file.filename,
                    "error": str(e),
                    "detection_count": 0,
                    "detections": []
                })
        
        # 生成巡检总结
        summary = {
            "route_id": route_id,
            "total_images": len(files),
            "processed_images": len([r for r in patrol_results if "error" not in r]),
            "failed_images": len([r for r in patrol_results if "error" in r]),
            "total_detections": total_detections,
            "average_detections_per_image": round(total_detections / len(files), 2) if files else 0,
            "processing_time": datetime.now().isoformat()
        }
        
        log.info(f"巡检完成: 总计 {len(files)} 张, 检测到 {total_detections} 个对象")
        
        return DetectionResult(
            code=0,
            msg="巡检完成",
            data={
                "summary": summary,
                "results": patrol_results
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"巡检失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"巡检失败: {str(e)}")

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
                "created_at": record.created_at.isoformat() if record.created_at else None
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

@router.get("/latest")
async def get_latest_detection(db=Depends(get_db)):
    """
    获取最新的检测记录（供3D模型页面使用）
    :return: 最新检测结果
    """
    try:
        # 获取最新的检测记录
        record = db.query(DetectionRecord).order_by(
            DetectionRecord.created_at.desc()
        ).first()
        
        if not record:
            return {
                "code": 0,
                "msg": "暂无检测记录",
                "data": None
            }
        
        # 返回检测记录
        return {
            "code": 0,
            "msg": "查询成功",
            "data": {
                "id": record.id,
                "filename": record.filename,
                "original_name": record.original_name,
                "vehicle_type": record.vehicle_type,
                "detection_count": record.detection_count,
                "confidence_score": record.confidence_score,
                "report": record.report_content,
                "detections": record.detections,  # 新增：返回完整的检测结果
                "created_at": record.created_at.isoformat(),
                "image_url": f"/static/upload/{record.filename}"
            }
        }
    except Exception as e:
        log.error(f"查询最新检测记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")

@router.get("/statistics")
async def get_statistics(db=Depends(get_db)):
    """
    获取检测统计数据
    :return: 统计信息
    """
    try:
        from sqlalchemy import func
        
        # 总记录数
        total_records = db.query(DetectionRecord).count()
        
        # 各车辆类型统计
        type_stats = db.query(
            DetectionRecord.vehicle_type,
            func.count(DetectionRecord.id).label('count'),
            func.avg(DetectionRecord.confidence_score).label('avg_confidence')
        ).group_by(DetectionRecord.vehicle_type).all()
        
        # 最近7天检测趋势
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_records = db.query(
            func.date(DetectionRecord.created_at).label('date'),
            func.count(DetectionRecord.id).label('count')
        ).filter(
            DetectionRecord.created_at >= seven_days_ago
        ).group_by(
            func.date(DetectionRecord.created_at)
        ).order_by(
            func.date(DetectionRecord.created_at)
        ).all()
        
        # 平均置信度
        avg_confidence_result = db.query(
            func.avg(DetectionRecord.confidence_score)
        ).scalar()
        avg_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0
        
        # 最高/最低置信度
        max_confidence_result = db.query(
            func.max(DetectionRecord.confidence_score)
        ).scalar()
        min_confidence_result = db.query(
            func.min(DetectionRecord.confidence_score)
        ).scalar()
        
        return {
            "code": 0,
            "msg": "查询成功",
            "data": {
                "total_records": total_records,
                "average_confidence": round(avg_confidence, 4),
                "max_confidence": round(float(max_confidence_result or 0), 4),
                "min_confidence": round(float(min_confidence_result or 0), 4),
                "type_distribution": [
                    {
                        "vehicle_type": row.vehicle_type,
                        "count": row.count,
                        "avg_confidence": round(float(row.avg_confidence or 0), 4)
                    }
                    for row in type_stats
                ],
                "recent_trend": [
                    {
                        "date": str(row.date),
                        "count": row.count
                    }
                    for row in recent_records
                ]
            }
        }
    except Exception as e:
        log.error(f"查询统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


def perform_damage_assessment(detections: list, description: Optional[str] = None) -> dict:
    """
    执行定损评估
    :param detections: YOLO检测结果列表
    :param description: 用户描述的损伤情况
    :return: 定损评估结果
    """
    if not detections:
        return {
            "severity_level": "轻微",
            "severity_score": 0,
            "estimated_cost_range": "0-500元",
            "repair_suggestion": "未发现明显损伤，建议定期保养",
            "safety_risk": "低",
            "urgency": "无需紧急处理"
        }
    
    # 基于检测数量和置信度计算严重程度
    detection_count = len(detections)
    avg_confidence = sum(d['confidence'] for d in detections) / detection_count if detections else 0
    
    # 简单的定损规则引擎
    if detection_count >= 5 or avg_confidence > 0.8:
        severity_level = "严重"
        severity_score = 4
        cost_range = "3000-10000元"
        repair_suggestion = "建议立即送修，可能存在结构性损伤"
        safety_risk = "高"
        urgency = "需紧急处理"
    elif detection_count >= 3 or avg_confidence > 0.6:
        severity_level = "中等"
        severity_score = 3
        cost_range = "1000-3000元"
        repair_suggestion = "建议尽快安排维修"
        safety_risk = "中"
        urgency = "建议近期处理"
    elif detection_count >= 1 or avg_confidence > 0.4:
        severity_level = "轻微"
        severity_score = 2
        cost_range = "500-1000元"
        repair_suggestion = "可根据实际情况安排维修"
        safety_risk = "低"
        urgency = "可择期处理"
    else:
        severity_level = "极轻微"
        severity_score = 1
        cost_range = "0-500元"
        repair_suggestion = "建议观察，下次保养时检查"
        safety_risk = "极低"
        urgency = "无需紧急处理"
    
    # 生成详细建议
    damage_types = [d['type'] for d in detections]
    locations = [d['location'] for d in detections]
    
    detailed_analysis = f"检测到 {detection_count} 处损伤，主要分布在{', '.join(set(locations))}。"
    
    return {
        "severity_level": severity_level,
        "severity_score": severity_score,
        "estimated_cost_range": cost_range,
        "repair_suggestion": repair_suggestion,
        "safety_risk": safety_risk,
        "urgency": urgency,
        "detection_count": detection_count,
        "average_confidence": round(avg_confidence, 4),
        "damage_types": damage_types,
        "locations": locations,
        "detailed_analysis": detailed_analysis,
        "user_description": description
    }
