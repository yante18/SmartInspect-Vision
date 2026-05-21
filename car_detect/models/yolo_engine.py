import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from utils.logger import log
from config import settings
from typing import List, Dict

class CarDamageDetector:
    """车损检测核心引擎（支持配置化阈值与降级策略）"""
    
    def __init__(self, model_path: str = None):
        # 默认使用 YOLOv8n 预训练模型（检测80类常见物体，包括汽车）
        self.model_name = "yolov8n.pt"
        self.conf_threshold = 0.5  # 置信度阈值
        
        try:
            log.info(f"[YOLO] 正在加载模型: {self.model_name}")
            self.model = YOLO(self.model_name)
            self.is_deployed = True
            log.info(f"[YOLO] 模型加载成功")
        except Exception as e:
            log.error(f"[YOLO] 模型加载失败: {e}，进入降级模式")
            self.is_deployed = False
            
    def detect(self, image_path: str) -> List[Dict]:
        """
        执行车辆/车损检测
        :param image_path: 图片路径
        :return: 检测结果列表
        """
        if not self.is_deployed:
            return [{
                "type": "未知",
                "location": "未识别",
                "confidence": 0.0,
                "bbox": [0, 0, 0, 0],
                "3d_position": {"x": 0, "y": 1.0, "z": 0}
            }]
             
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
            
        height, width = img.shape[:2]
        
        # 执行 YOLO 推理
        results = self.model(img, conf=self.conf_threshold, iou=0.45)[0]
        
        damage_list = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = results.names[cls_id]
            conf = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            
            # 中文映射与位置计算
            damage_type = self._map_class(cls_name)
            location = self._get_location(bbox, width, height)
            pos_3d = self._compute_3d_position(location, bbox, width, height)
            
            damage_list.append({
                "type": damage_type,
                "location": location,
                "confidence": round(conf, 2),
                "bbox": [round(x) for x in bbox],
                "3d_position": pos_3d,
                "class_name": cls_name
            })
            
        log.info(f"[YOLO] 检测到 {len(damage_list)} 个对象")
        return damage_list

    def _map_class(self, cls: str) -> str:
        """类别名称中文映射"""
        # YOLOv8 COCO 数据集类别映射
        map_cn = {
            "car": "汽车",
            "truck": "卡车",
            "bus": "公交车",
            "motorcycle": "摩托车",
            "bicycle": "自行车",
            "person": "行人"
        }
        return map_cn.get(cls, cls)

    def _get_location(self, bbox: list, w: int, h: int) -> str:
        """根据 bbox 计算损伤位置"""
        cx, cy = (bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2
        if cx < w*0.3: 
            return "左侧"
        elif cx > w*0.7: 
            return "右侧"
        elif cy < h*0.4: 
            return "前部"
        elif cy > h*0.6: 
            return "后部"
        else: 
            return "中部"

    def _compute_3d_position(self, loc: str, bbox: list, w: int, h: int) -> dict:
        """
        计算3D位置（启发式算法）
        实际项目需替换为相机标定+地面平面假设
        """
        base = {
            "前部": (2.0, 1.0, 0),
            "后部": (-2.0, 1.0, 0),
            "左侧": (0, 1.0, 1.5),
            "右侧": (0, 1.0, -1.5),
            "中部": (0, 1.0, 0)
        }
        bx, by, bz = base.get(loc, (0, 1.0, 0))
        
        # 基于bbox相对图像中心的偏移补偿
        rx = ((bbox[0]+bbox[2])/2 / w - 0.5) * 0.6
        ry = (1 - (bbox[1]+bbox[3])/2 / h) * 0.4
        return {
            "x": round(bx+rx, 2),
            "y": round(by+ry, 2),
            "z": round(bz, 2)
        }

    def detect_and_draw(self, image_path: str, output_path: str = None) -> str:
        """
        检测并在图片上绘制结果
        :param image_path: 输入图片路径
        :param output_path: 输出图片路径（可选）
        :return: 输出图片路径
        """
        if not output_path:
            output_path = str(Path(image_path).parent / f"result_{Path(image_path).name}")
        
        # 执行推理
        results = self.model(image_path, conf=self.conf_threshold)
        
        # 绘制结果
        result_img = results[0].plot()
        
        # 保存图片
        cv2.imwrite(output_path, result_img)
        log.info(f"[YOLO] 检测结果已保存: {output_path}")
        
        return output_path


# 全局单例
_detector = None

def get_detector() -> CarDamageDetector:
    """获取检测器单例"""
    global _detector
    if _detector is None:
        _detector = CarDamageDetector()
    return _detector
