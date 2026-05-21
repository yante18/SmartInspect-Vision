"""
YOLO 模型测试脚本
用于验证 YOLOv8 检测功能是否正常
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from models.yolo_engine import get_detector
from utils.logger import log

def test_yolo_detection():
    """测试 YOLO 检测功能"""
    print("=" * 60)
    print("🧪 YOLO 模型测试")
    print("=" * 60)
    
    # 1. 初始化检测器
    print("\n[1] 初始化检测器...")
    try:
        detector = get_detector()
        print(f"✅ 检测器初始化成功")
        print(f"   - 模型名称: {detector.model_name}")
        print(f"   - 置信度阈值: {detector.conf_threshold}")
        print(f"   - 部署状态: {'已部署' if detector.is_deployed else '降级模式'}")
    except Exception as e:
        print(f"❌ 检测器初始化失败: {e}")
        return False
    
    # 2. 查找测试图片
    print("\n[2] 查找测试图片...")
    upload_dir = Path(__file__).parent / "static" / "upload"
    test_images = list(upload_dir.glob("*.jpg")) + list(upload_dir.glob("*.png"))
    
    if not test_images:
        print(f"⚠️  未找到测试图片，请在 {upload_dir} 放置测试图片")
        print("   或使用以下命令下载测试图片:")
        print("   curl -o static/upload/test.jpg https://ultralytics.com/assets/bus.jpg")
        return False
    
    test_image = test_images[0]
    print(f"✅ 找到测试图片: {test_image.name}")
    
    # 3. 执行检测
    print("\n[3] 执行 YOLO 检测...")
    try:
        results = detector.detect(str(test_image))
        print(f"✅ 检测完成")
        print(f"   - 检测到 {len(results)} 个对象")
        
        if results:
            print("\n📊 检测结果详情:")
            for i, result in enumerate(results, 1):
                print(f"   [{i}] 类型: {result['type']}")
                print(f"       位置: {result['location']}")
                print(f"       置信度: {result['confidence']:.2f}")
                print(f"       类别: {result.get('class_name', 'N/A')}")
                print(f"       3D坐标: x={result['3d_position']['x']}, y={result['3d_position']['y']}, z={result['3d_position']['z']}")
                print(f"       BBox: {result['bbox']}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ 检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_yolo_detection()
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试通过！YOLO 模型工作正常")
    else:
        print("❌ 测试失败！请检查配置和依赖")
    print("=" * 60)
    sys.exit(0 if success else 1)
