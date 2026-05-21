"""
分布式架构测试脚本
用于验证本地服务和云端连接是否正常
"""
import sys
from pathlib import Path
import requests
import time

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from config import settings

def test_local_service():
    """测试本地 YOLO 服务"""
    print("=" * 60)
    print("🧪 测试本地 YOLO 服务")
    print("=" * 60)
    
    base_url = "http://localhost:9000"
    
    # 1. 健康检查
    print("\n[1] 健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务正常")
            print(f"   - 模型加载: {data.get('detector_loaded')}")
            print(f"   - 模型名称: {data.get('model_name')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print(f"   提示: 请先启动本地服务 (python local_yolo_service.py)")
        return False
    
    # 2. 查找测试图片
    print("\n[2] 查找测试图片...")
    upload_dir = Path(__file__).parent / "static" / "upload"
    test_images = list(upload_dir.glob("*.jpg")) + list(upload_dir.glob("*.png"))
    
    if not test_images:
        print(f"⚠️  未找到测试图片")
        return False
    
    test_image = test_images[0]
    print(f"✅ 使用图片: {test_image.name}")
    
    # 3. 测试检测接口
    print("\n[3] 测试检测接口...")
    try:
        with open(test_image, "rb") as f:
            files = {"file": (test_image.name, f, "image/jpeg")}
            headers = {"X-API-Token": settings.YOLO_API_TOKEN}
            
            response = requests.post(
                f"{base_url}/detect",
                files=files,
                headers=headers,
                timeout=30
            )
        
        if response.status_code != 200:
            print(f"❌ 检测失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return False
        
        result = response.json()
        
        if result.get("code") != 0:
            print(f"❌ 检测失败: {result.get('msg')}")
            return False
        
        detections = result.get("data", {}).get("results", [])
        print(f"✅ 检测成功")
        print(f"   - 检测到 {len(detections)} 个对象")
        
        if detections:
            print("\n📊 检测结果:")
            for i, det in enumerate(detections[:3], 1):  # 只显示前3个
                print(f"   [{i}] {det['type']} - 置信度: {det['confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检测异常: {e}")
        return False

def test_remote_connection():
    """测试远程连接（从云端视角）"""
    print("\n" + "=" * 60)
    print("🌐 测试远程连接配置")
    print("=" * 60)
    
    print(f"\n当前配置:")
    print(f"  - USE_REMOTE_YOLO: {settings.USE_REMOTE_YOLO}")
    print(f"  - REMOTE_YOLO_URL: {settings.REMOTE_YOLO_URL}")
    print(f"  - YOLO_API_TOKEN: {'***' + settings.YOLO_API_TOKEN[-4:] if settings.YOLO_API_TOKEN else '未设置'}")
    
    if not settings.USE_REMOTE_YOLO:
        print("\n⚠️  当前使用本地推理模式")
        print("   如需测试远程调用，请设置 USE_REMOTE_YOLO=true")
        return True
    
    # 测试远程连接
    print(f"\n[1] 测试远程连接: {settings.REMOTE_YOLO_URL}")
    try:
        response = requests.get(
            f"{settings.REMOTE_YOLO_URL}/health",
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ 远程服务可达")
            return True
        else:
            print(f"❌ 远程服务异常: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 无法连接到远程服务: {e}")
        print(f"\n💡 排查建议:")
        print(f"   1. 确认本地服务已启动")
        print(f"   2. 检查内网穿透隧道是否运行")
        print(f"   3. 验证防火墙/安全组规则")
        print(f"   4. 确认 URL 和 Token 配置正确")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 SmartInspect-Vision 分布式架构测试")
    print("=" * 60)
    
    # 测试本地服务
    local_ok = test_local_service()
    
    # 测试远程连接
    remote_ok = test_remote_connection()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"  本地服务: {'✅ 通过' if local_ok else '❌ 失败'}")
    print(f"  远程连接: {'✅ 通过' if remote_ok else '❌ 失败'}")
    print("=" * 60)
    
    if local_ok and remote_ok:
        print("\n🎉 所有测试通过！系统已就绪")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查配置")
        sys.exit(1)
