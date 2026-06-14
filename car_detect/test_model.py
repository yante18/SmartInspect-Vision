#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
车损模型测试脚本
"""
import sys
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from models.yolo_engine import get_detector
from utils.logger import log

def test_model_loading():
    """测试模型加载"""
    print("=" * 60)
    print("🚀 开始测试 YOLO 模型加载")
    print("=" * 60)
    
    try:
        detector = get_detector()
        if detector.is_deployed:
            print("✅ 模型加载成功！")
            print(f"📁 使用模型: {detector.model_name}")
            print(f"🔧 置信度阈值: {detector.conf_threshold}")
            print(f"🎯 IOU 阈值: {detector.iou_threshold}")
            print(f"📋 支持类别数: {len(detector.class_names)}")
            return True
        else:
            print("❌ 模型加载失败，请检查配置")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_detection():
    """测试模型检测功能"""
    print("\n" + "=" * 60)
    print("🔍 开始测试模型检测功能")
    print("=" * 60)
    
    # 查找测试图片
    test_images = list(Path("datasets/car-damage-dataset/images").glob("*.*"))
    if not test_images:
        print("⚠️  未找到测试图片，请先导入数据集")
        return False
    
    print(f"📁 找到 {len(test_images)} 张测试图片")
    
    detector = get_detector()
    if not detector.is_deployed:
        print("❌ 模型未加载，跳过检测测试")
        return False
    
    # 测试一张图片
    test_img = test_images[0]
    print(f"📷  测试图片: {test_img}")
    
    try:
        results = detector.detect(str(test_img))
        print(f"✅ 检测完成！")
        print(f"📋 检测到 {len(results)} 个对象")
        
        for i, damage in enumerate(results, 1):
            print(f"\n--- 损伤 {i}:")
            print(f"    🔧 类型: {damage['type']}")
            print(f"    📍 位置: {damage['location']}")
            print(f"    📊 置信度: {damage['confidence']}")
            print(f"    📦 边界框: {damage['bbox']}")
        
        return True
    except Exception as e:
        print(f"❌ 检测测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dataset_info():
    """检查数据集信息"""
    print("\n" + "=" * 60)
    print("📁 数据集信息检查")
    print("=" * 60)
    
    dataset_root = Path("datasets/car-damage-dataset")
    if not dataset_root.exists():
        print("❌ 数据集目录不存在")
        return False
    
    print(f"📁 数据集目录: {dataset_root}")
    
    train_images = list((dataset_root / "images/train").glob("*.*")) if (dataset_root / "images/train").exists() else []
    val_images = list((dataset_root / "images/val").glob("*.*")) if (dataset_root / "images/val").exists() else []
    train_labels = list((dataset_root / "labels/train").glob("*.txt")) if (dataset_root / "labels/train").exists() else []
    val_labels = list((dataset_root / "labels/val").glob("*.txt")) if (dataset_root / "labels/val").exists() else []
    
    print(f"📊 训练集: {len(train_images)} 张图片, {len(train_labels)} 个标注")
    print(f"📊 验证集: {len(val_images)} 张图片, {len(val_labels)} 个标注")
    
    return True

def main():
    """主函数"""
    print("\n🎯 智检慧眼 - 车损检测系统测试\n")
    
    # 检查数据集
    dataset_ok = check_dataset_info()
    
    # 测试模型加载
    load_ok = test_model_loading()
    
    # 测试检测功能
    if load_ok and dataset_ok:
        detect_ok = test_model_detection()
    else:
        detect_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    print(f"✅ 数据集检查: {'通过' if dataset_ok else '失败'}")
    print(f"✅ 模型加载: {'通过' if load_ok else '失败'}")
    print(f"✅ 检测功能: {'通过' if detect_ok else '失败'}")
    
    if dataset_ok and load_ok and detect_ok:
        print("\n🎉 所有测试通过！系统已准备就绪！")
        print("🚀 现在可以运行 python main.py 启动服务")
    else:
        print("\n⚠️  部分测试失败，请检查问题")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 测试已中断")
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
