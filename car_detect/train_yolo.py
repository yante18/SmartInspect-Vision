"""
YOLOv8 车损检测模型训练脚本

使用方法:
    python train_yolo.py --epochs 100 --batch 16 --imgsz 640

参数说明:
    --epochs: 训练轮数
    --batch: 批次大小
    --imgsz: 输入图片尺寸
    --device: 使用 GPU(0) 或 CPU(cpu)
"""

import argparse
from ultralytics import YOLO
from pathlib import Path


def train_yolo(epochs=100, batch=16, imgsz=640, device='0'):
    """训练 YOLOv8 车损检测模型"""
    
    # 创建训练输出目录
    Path("runs/detect").mkdir(parents=True, exist_ok=True)
    
    # 加载预训练模型（推荐使用 yolov8n.pt 作为基础）
    print("🔄 加载预训练模型: yolov8n.pt")
    model = YOLO("yolov8n.pt")
    
    # 开始训练
    print(" 开始训练...")
    results = model.train(
        data="car_damage.yaml",      # 数据集配置文件
        epochs=epochs,                # 训练轮数
        batch=batch,                  # 批次大小
        imgsz=imgsz,                  # 图片尺寸
        device=device,                # 设备
        workers=8,                    # 数据加载线程数
        project="runs/detect",        # 输出项目目录
        name="car_damage_v1",         # 实验名称
        patience=15,                  # 早停耐心值
        amp=True,                     # 混合精度训练
        cache="ram",                  # 缓存到内存加速
        # 数据增强参数
        degrees=5,                    # 旋转角度
        translate=0.2,                # 平移比例
        scale=0.5,                    # 缩放范围
        fliplr=0.5,                   # 水平翻转概率
        flipud=0.0,                   # 垂直翻转概率
        mosaic=1.0,                   # Mosaic 增强
        # 训练优化
        lr0=0.01,                     # 初始学习率
        lrf=0.01,                     # 最终学习率比例
        momentum=0.937,               # SGD momentum
        weight_decay=0.0005,          # 权重衰减
        # 其他参数
        verbose=True,                 # 详细日志
        plots=True,                   # 生成训练曲线图
    )
    
    # 训练完成后保存最佳模型
    best_model_path = Path("runs/detect/car_damage_v1/weights/best.pt")
    if best_model_path.exists():
        # 复制到项目根目录方便使用
        import shutil
        shutil.copy(best_model_path, "car_damage_best.pt")
        print(f"\n✅ 训练完成！最佳模型已保存到: car_damage_best.pt")
        print(f"📊 详细训练日志: runs/detect/car_damage_v1/")
        
        # 测试训练的模型
        print("\n🧪 测试训练后的模型...")
        model = YOLO("car_damage_best.pt")
        metrics = model.val()
        print(f"📈 mAP@0.5: {metrics.box.map50:.4f}")
        print(f"📈 mAP@0.5-0.95: {metrics.box.map:.4f}")
    
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLOv8 车损检测模型训练")
    parser.add_argument("--epochs", type=int, default=100, help="训练轮数")
    parser.add_argument("--batch", type=int, default=16, help="批次大小")
    parser.add_argument("--imgsz", type=int, default=640, help="图片尺寸")
    parser.add_argument("--device", type=str, default="0", help="设备 (0=GPU, cpu=CPU)")
    
    args = parser.parse_args()
    
    train_yolo(
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device
    )
