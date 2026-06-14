"""
YOLOv8 车损检测模型训练脚本
使用 car_damage.yaml 配置文件训练
"""

from ultralytics import YOLO
import os
from pathlib import Path

def train_model():
    """训练 YOLOv8 车损检测模型"""
    
    print("=" * 60)
    print("🚀 开始训练 YOLOv8 车损检测模型")
    print("=" * 60)
    
    # 项目根目录
    project_root = Path(__file__).parent
    
    # 配置文件路径
    config_file = project_root / "car_damage.yaml"
    
    if not config_file.exists():
        print(f" 错误：配置文件不存在 {config_file}")
        return
    
    print(f"✅ 配置文件：{config_file}")
    
    # 加载预训练模型（使用 YOLOv8n）
    print("\n📦 加载预训练模型 yolov8n.pt...")
    model = YOLO("yolov8n.pt")
    
    # 训练参数配置
    training_args = {
        'data': str(config_file),           # 数据集配置文件
        'epochs': 100,                       # 训练轮数（建议至少 100）
        'batch': 8,                          # 批次大小（根据显存调整：8-16）
        'imgsz': 640,                        # 输入图片尺寸
        'device': '0',                       # 使用 GPU 0（如果有 GPU）
        'workers': 4,                        # 数据加载线程数
        'project': str(project_root / 'runs'),  # 项目保存目录
        'name': 'car_damage_yolov8n',        # 实验名称
        'exist_ok': True,                    # 覆盖已存在的实验
        'patience': 20,                      # 早停耐心值
        'save': True,                        # 保存模型检查点
        'save_period': 10,                   # 每 N 个 epoch 保存一次
        'cache': False,                      # 是否缓存图片到内存
        'optimizer': 'SGD',                  # 优化器
        'lr0': 0.01,                         # 初始学习率
        'lrf': 0.01,                         # 最终学习率
        'momentum': 0.937,                   # SGD 动量
        'weight_decay': 0.0005,              # 权重衰减
        'warmup_epochs': 3.0,                # 热身轮数
        'warmup_momentum': 0.8,              # 热身动量
        'warmup_bias_lr': 0.1,               # 热身偏置学习率
        'box': 7.5,                          # box loss 权重
        'cls': 0.5,                          # classification loss 权重
        'dfl': 1.5,                          # DFL loss 权重
        'val': True,                         # 训练期间验证
        'plots': True,                       # 保存训练图表
        'augment': True,                     # 数据增强
        'verbose': True,                     # 详细日志
    }
    
    print("\n" + "=" * 60)
    print("📋 训练配置")
    print("=" * 60)
    print(f"模型：YOLOv8n（Nano 版本）")
    print(f"数据集配置文件：car_damage.yaml")
    print(f"训练轮数：{training_args['epochs']}")
    print(f"批次大小：{training_args['batch']}")
    print(f"图片尺寸：{training_args['imgsz']}")
    print(f"设备：{'CPU' if training_args['device'] == 'cpu' else 'GPU ' + training_args['device']}")
    print(f"优化器：{training_args['optimizer']}")
    print(f"初始学习率：{training_args['lr0']}")
    print(f"早停耐心值：{training_args['patience']}")
    print("=" * 60)
    
    print("\n⏳ 开始训练，请稍候...")
    print("（训练过程中会显示每轮的损失和指标）\n")
    
    try:
        # 开始训练
        results = model.train(**training_args)
        
        print("\n" + "=" * 60)
        print("✅ 训练完成！")
        print("=" * 60)
        
        # 显示结果路径
        results_dir = project_root / "runs" / "car_damage_yolov8n"
        best_model = results_dir / "weights" / "best.pt"
        last_model = results_dir / "weights" / "last.pt"
        
        print(f"📁 结果目录：{results_dir}")
        print(f"🏆 最佳模型：{best_model}")
        print(f"💾 最新模型：{last_model}")
        print(f" 训练图表：{results_dir / 'results.png'}")
        print(f" 混淆矩阵：{results_dir / 'confusion_matrix.png'}")
        print(f"🎯 验证结果：{results_dir / 'val_batch0_pred.jpg'}")
        
        if best_model.exists():
            print(f"\n✨ 最佳模型大小：{best_model.stat().st_size / (1024*1024):.2f} MB")
        
        print("\n" + "=" * 60)
        print(" 下一步建议")
        print("=" * 60)
        print("1. 验证模型性能：python train_yolo.py --validate")
        print("2. 测试模型效果：python train_yolo.py --test")
        print("3. 导出模型格式：python train_yolo.py --export")
        print("4. 查看详细结果：打开 runs/car_damage_yolov8n/ 目录")
        print("=" * 60)
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 训练被用户中断")
        print("已保存的模型可在 runs/car_damage_yolov8n/weights/ 中找到")
        return None
        
    except Exception as e:
        print(f"\n❌ 训练失败：{e}")
        import traceback
        traceback.print_exc()
        return None

def validate_model():
    """验证训练好的模型"""
    
    print("\n" + "=" * 60)
    print("🔍 验证模型性能")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    best_model = project_root / "runs" / "car_damage_yolov8n" / "weights" / "best.pt"
    
    if not best_model.exists():
        print(f"❌ 模型文件不存在：{best_model}")
        print("请先运行训练：python train_yolo.py")
        return
    
    print(f"✅ 加载模型：{best_model}")
    model = YOLO(str(best_model))
    
    print("\n⏳ 开始验证...\n")
    
    try:
        results = model.val(
            data=str(project_root / "car_damage.yaml"),
            batch=8,
            imgsz=640,
            device='0',
            split='val',
            plots=True,
            verbose=True
        )
        
        print("\n" + "=" * 60)
        print("📊 验证结果")
        print("=" * 60)
        print(f"mAP50:      {results.box.map50:.4f}")
        print(f"mAP50-95:   {results.box.map:.4f}")
        print(f"Precision:  {results.box.mp:.4f}")
        print(f"Recall:     {results.box.mr:.4f}")
        print("=" * 60)
        
        print("\n💡 指标说明：")
        print("  • mAP50: IoU=0.5 时的平均精度（越接近 1 越好）")
        print("  • mAP50-95: IoU=0.5-0.95 的平均精度（综合指标）")
        print("  • Precision: 精确率（预测为正的中有多少是真的正）")
        print("  • Recall: 召回率（所有正样本中有多少被正确预测）")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 验证失败：{e}")
        import traceback
        traceback.print_exc()

def test_model(image_path=None):
    """测试模型效果"""
    
    print("\n" + "=" * 60)
    print(" 测试模型效果")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    best_model = project_root / "runs" / "car_damage_yolov8n" / "weights" / "best.pt"
    
    if not best_model.exists():
        print(f" 模型文件不存在：{best_model}")
        return
    
    # 加载模型
    model = YOLO(str(best_model))
    
    # 如果没有指定图片，使用数据集中的一张
    if image_path is None:
        datasets_dir = project_root / "datasets" / "car-damage-dataset" / "images"
        # 尝试找到一张图片
        for img_file in datasets_dir.glob("*.jpg"):
            image_path = str(img_file)
            break
        if image_path is None:
            print("❌ 未找到测试图片")
            return
    
    print(f"📷 测试图片：{image_path}")
    print("\n⏳ 开始检测...\n")
    
    try:
        # 执行检测
        results = model.predict(
            source=image_path,
            imgsz=640,
            conf=0.25,    # 置信度阈值
            iou=0.45,     # NMS IoU 阈值
            save=True,    # 保存结果图片
            project=str(project_root / "runs" / "predictions"),
            name="test_result",
            exist_ok=True
        )
        
        # 显示检测结果
        result = results[0]
        print("\n" + "=" * 60)
        print("📊 检测结果")
        print("=" * 60)
        print(f"检测到的目标数量：{len(result.boxes)}")
        
        for i, box in enumerate(result.boxes):
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]
            print(f"  目标 {i+1}: {class_name} (置信度: {confidence:.2%})")
        
        print("\n 结果图片已保存至：")
        print(f"   runs/predictions/test_result/")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()

def export_model():
    """导出模型为其他格式"""
    
    print("\n" + "=" * 60)
    print("📦 导出模型")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    best_model = project_root / "runs" / "car_damage_yolov8n" / "weights" / "best.pt"
    
    if not best_model.exists():
        print(f"❌ 模型文件不存在：{best_model}")
        return
    
    print(f"✅ 加载模型：{best_model}")
    model = YOLO(str(best_model))
    
    # 导出为 ONNX 格式（推荐）
    print("\n📤 导出为 ONNX 格式...")
    try:
        model.export(format='onnx', imgsz=640, simplify=True, opset=12)
        print("✅ ONNX 导出成功")
    except Exception as e:
        print(f"️ ONNX 导出失败：{e}")
    
    # 导出为 TorchScript
    print("\n📤 导出为 TorchScript 格式...")
    try:
        model.export(format='torchscript', imgsz=640)
        print("✅ TorchScript 导出成功")
    except Exception as e:
        print(f"⚠️ TorchScript 导出失败：{e}")
    
    print("\n" + "=" * 60)
    print("导出完成！")
    print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLOv8 车损检测模型训练脚本')
    parser.add_argument('--train', action='store_true', help='训练模型（默认）')
    parser.add_argument('--validate', action='store_true', help='验证模型')
    parser.add_argument('--test', action='store_true', help='测试模型')
    parser.add_argument('--export', action='store_true', help='导出模型')
    parser.add_argument('--image', type=str, help='测试图片路径（用于 --test）')
    
    args = parser.parse_args()
    
    # 默认行为：训练模型
    if not any([args.train, args.validate, args.test, args.export]):
        args.train = True
    
    if args.train:
        train_model()
    
    if args.validate:
        validate_model()
    
    if args.test:
        test_model(args.image)
    
    if args.export:
        export_model()
