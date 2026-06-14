import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from utils.logger import log
from config import settings
from typing import List, Dict

class CarDamageDetector:
    """车损检测核心引擎（支持配置化阈值与降级策略）"""
    
    # 车损类别名称映射（34类）
    DAMAGE_CLASSES = [
        "车门与翼子板的接缝处错位",
        "后翼子板撕裂",
        "车漆刮擦破损",
        "车门与翼子板的接线处错位",
        "车门撕裂",
        "车门大面积凹陷",
        "中网损坏",
        "前保险杠脱落",
        "车灯支架损坏",
        "后保险杠撕裂破损",
        "尾灯灯罩破损",
        "前挡风玻璃破损",
        "引擎盖翘起变形",
        "车灯破损",
        "后保险杠损坏",
        "车尾严重溃缩变形",
        "排气系统脱落",
        "翼子板撕裂",
        "翼子板凹陷",
        "翼子板撕裂、凹陷",
        "水箱框架、前纵梁严重溃缩变形",
        "后备箱盖损坏",
        "后翼子板脱落",
        "车顶凹陷",
        "线束外露",
        "后备箱盖溃缩变形",
        "排气管外露",
        "水箱框架外露",
        "保险杠撕裂",
        "轮毂、悬挂部件损坏",
        "轮胎脱落",
        "后保险杠脱落",
        "车门凹陷",
        "前保险杠撕裂"
    ]
    
    def __init__(self, model_path: str = None):
        # 优先使用配置中指定的模型
        if model_path:
            self.model_name = model_path
        else:
            self.model_name = str(settings.BASE_DIR / settings.YOLO_MODEL_PATH)
        
        self.conf_threshold = settings.YOLO_CONF_THRESHOLD
        self.iou_threshold = settings.YOLO_IOU_THRESHOLD
        self.is_deployed = False
        self.model = None
        self.class_names = self.DAMAGE_CLASSES
        
        # 尝试加载训练好的模型
        try:
            if Path(self.model_name).exists():
                log.info(f"[YOLO] 正在加载训练模型: {self.model_name}")
                self.model = YOLO(self.model_name)
                self.is_deployed = True
                log.info(f"[YOLO] 训练模型加载成功！")
            else:
                log.warning(f"[YOLO] 训练模型不存在，尝试加载备用模型")
                self._load_fallback_model()
        except Exception as e:
            log.error(f"[YOLO] 模型加载失败: {e}，尝试加载备用模型")
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """加载备用的预训练模型"""
        try:
            fallback_path = str(settings.BASE_DIR / settings.YOLO_FALLBACK_PATH)
            log.info(f"[YOLO] 正在加载备用模型: {fallback_path}")
            self.model = YOLO(fallback_path)
            self.is_deployed = True
            log.warning(f"[YOLO] 使用备用模型，部分功能可能受限")
        except Exception as e:
            log.error(f"[YOLO] 备用模型也加载失败: {e}")
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
        results = self.model(img, conf=self.conf_threshold, iou=self.iou_threshold)[0]
        
        damage_list = []
        for box in results.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            bbox = box.xyxy[0].tolist()
            
            # 获取类别名称（优先使用训练模型的类别）
            damage_type = self._get_class_name(cls_id, results.names)
            location = self._get_location(bbox, width, height)
            pos_3d = self._compute_3d_position(damage_type, location, bbox, width, height)
            
            damage_list.append({
                "type": damage_type,
                "location": location,
                "confidence": round(conf, 2),
                "bbox": [round(x) for x in bbox],
                "3d_position": pos_3d,
                "class_id": cls_id
            })
            
        log.info(f"[YOLO] 检测到 {len(damage_list)} 个车损")
        return damage_list

    def _get_class_name(self, cls_id: int, names_dict: dict) -> str:
        """获取类别名称"""
        # 优先使用我们预定义的 34 类车损名称
        if cls_id < len(self.DAMAGE_CLASSES):
            return self.DAMAGE_CLASSES[cls_id]
        # 否则使用模型返回的名称
        return names_dict.get(cls_id, f"类别_{cls_id}")

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

    def _compute_3d_position(self, damage_type: str, loc: str, bbox: list, w: int, h: int) -> dict:
        """
        计算3D位置（基于损伤类型的精确映射）
        将34种损伤类型精确映射到小米SU7模型的对应位置
        """
        # 34种损伤类型的精确3D位置映射（小米SU7坐标系）
        DAMAGE_3D_POSITIONS = {
            # 前部损伤
            "车门与翼子板的接缝处错位": (1.2, 0.8, 1.2),
            "前保险杠脱落": (1.8, 0.3, 0),
            "中网损坏": (1.6, 0.6, 0),
            "车灯支架损坏": (1.5, 0.8, -0.6),
            "车灯破损": (1.5, 0.8, 0.6),
            "前保险杠撕裂": (1.7, 0.4, 0.5),
            "水箱框架、前纵梁严重溃缩变形": (1.2, 0.7, 0),
            "水箱框架外露": (1.0, 0.8, 0),
            
            # 后部损伤
            "后翼子板撕裂": (-1.2, 0.8, 1.2),
            "后保险杠撕裂破损": (-1.7, 0.4, 0),
            "尾灯灯罩破损": (-1.5, 0.8, 0.6),
            "后备箱盖损坏": (-1.3, 1.1, 0),
            "后备箱盖溃缩变形": (-1.1, 1.0, 0),
            "后保险杠损坏": (-1.8, 0.3, 0),
            "后保险杠脱落": (-1.9, 0.2, 0),
            "车尾严重溃缩变形": (-1.5, 0.9, 0),
            
            # 左侧损伤
            "车门撕裂": (0.3, 0.9, 1.3),
            "车门大面积凹陷": (0.2, 0.8, 1.2),
            "车门凹陷": (0.4, 0.7, 1.1),
            "翼子板撕裂": (0.8, 0.9, 1.4),
            "翼子板凹陷": (0.9, 0.8, 1.3),
            "翼子板撕裂、凹陷": (0.85, 0.85, 1.35),
            "后翼子板脱落": (-0.8, 0.9, 1.4),
            "轮毂、悬挂部件损坏": (0, 0.2, 1.2),
            "轮胎脱落": (0, 0.1, 1.3),
            
            # 右侧损伤
            "车门与翼子板的接线处错位": (1.2, 0.8, -1.2),
            "翼子板撕裂": (0.8, 0.9, -1.4),
            "翼子板凹陷": (0.9, 0.8, -1.3),
            "车门撕裂": (0.3, 0.9, -1.3),
            "车门凹陷": (0.4, 0.7, -1.1),
            
            # 中部/顶部损伤
            "车漆刮擦破损": (0, 0.8, 0),  # 通用位置
            "车顶凹陷": (0, 1.6, 0),
            "线束外露": (0, 0.5, 0.5),
            "排气管外露": (-1.4, 0.3, 0),
            "排气系统脱落": (-1.6, 0.2, 0),
            "前挡风玻璃破损": (0.8, 1.4, 0),
            "引擎盖翘起变形": (1.0, 1.2, 0)
        }
        
        # 优先使用损伤类型的精确位置
        if damage_type in DAMAGE_3D_POSITIONS:
            bx, by, bz = DAMAGE_3D_POSITIONS[damage_type]
        else:
            # 回退到基于位置的默认映射
            base = {
                "前部": (1.5, 0.9, 0),
                "后部": (-1.5, 0.9, 0),
                "左侧": (0, 0.9, 1.2),
                "右侧": (0, 0.9, -1.2),
                "中部": (0, 0.9, 0)
            }
            bx, by, bz = base.get(loc, (0, 0.9, 0))
        
        # 基于bbox相对图像中心的偏移做细微调整
        rx = ((bbox[0]+bbox[2])/2 / w - 0.5) * 0.3
        ry = (1 - (bbox[1]+bbox[3])/2 / h) * 0.2
        return {
            "x": round(bx + rx, 2),
            "y": round(by + ry, 2),
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
