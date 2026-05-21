"""
数据集准备脚本
用于创建标准的 YOLO 数据集目录结构和验证数据格式
"""

from pathlib import Path
import shutil
from PIL import Image


def prepare_dataset_structure():
    """创建数据集目录结构"""
    
    base_dir = Path("datasets/car-damage-dataset")
    
    # 创建必要的目录
    dirs = [
        base_dir / "images" / "train",
        base_dir / "images" / "val",
        base_dir / "labels" / "train",
        base_dir / "labels" / "val",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")
    
    print(f"\n📁 数据集结构已创建:")
    print(f"   {base_dir}/")
    print(f"   ├── images/")
    print(f"   │   ├── train/  # 放置训练集图片")
    print(f"   │   └── val/    # 放置验证集图片")
    print(f"   └── labels/")
    print(f"       ├── train/  # 放置训练集标注文件(.txt)")
    print(f"       └── val/    # 放置验证集标注文件(.txt)")
    
    return base_dir


def validate_annotation_format(label_file: Path) -> bool:
    """
    验证标注文件格式是否正确
    
    YOLO 格式要求:
    <class_id> <x_center> <y_center> <width> <height>
    所有坐标值必须是 0-1 之间的归一化值
    """
    
    if not label_file.exists():
        print(f"❌ 标注文件不存在: {label_file}")
        return False
    
    with open(label_file, 'r') as f:
        lines = f.readlines()
    
    if len(lines) == 0:
        print(f"⚠️  警告: 标注文件为空: {label_file}")
        return True  # 允许空标注（图片中无目标）
    
    for i, line in enumerate(lines, 1):
        parts = line.strip().split()
        
        if len(parts) != 5:
            print(f"❌ {label_file} 第 {i} 行格式错误，需要 5 个值，实际 {len(parts)} 个")
            return False
        
        try:
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # 验证类别 ID
            if not (0 <= class_id <= 3):
                print(f"❌ {label_file} 第 {i} 行: 类别 ID 应在 0-3 之间，实际 {class_id}")
                return False
            
            # 验证归一化坐标
            if not (0 <= x_center <= 1):
                print(f"❌ {label_file} 第 {i} 行: x_center 应在 0-1 之间，实际 {x_center}")
                return False
            if not (0 <= y_center <= 1):
                print(f"❌ {label_file} 第 {i} 行: y_center 应在 0-1 之间，实际 {y_center}")
                return False
            if not (0 < width <= 1):
                print(f"❌ {label_file} 第 {i} 行: width 应在 0-1 之间，实际 {width}")
                return False
            if not (0 < height <= 1):
                print(f"❌ {label_file} 第 {i} 行: height 应在 0-1 之间，实际 {height}")
                return False
            
        except ValueError as e:
            print(f" {label_file} 第 {i} 行: 数值转换失败 - {e}")
            return False
    
    return True


def validate_image_format(image_file: Path) -> bool:
    """验证图片格式"""
    
    if not image_file.exists():
        print(f"❌ 图片文件不存在: {image_file}")
        return False
    
    try:
        img = Image.open(image_file)
        img.verify()  # 验证图片完整性
        return True
    except Exception as e:
        print(f"❌ 图片格式错误: {image_file} - {e}")
        return False


def validate_dataset(dataset_dir: Path = None):
    """验证整个数据集"""
    
    if dataset_dir is None:
        dataset_dir = Path("datasets/car-damage-dataset")
    
    print(f"🔍 开始验证数据集: {dataset_dir}\n")
    
    # 验证训练集
    train_images = list((dataset_dir / "images" / "train").glob("*"))
    train_labels = list((dataset_dir / "labels" / "train").glob("*"))
    
    # 验证验证集
    val_images = list((dataset_dir / "images" / "val").glob("*"))
    val_labels = list((dataset_dir / "labels" / "val").glob("*"))
    
    print(f"📊 数据集统计:")
    print(f"   训练集图片: {len(train_images)} 张")
    print(f"   训练集标注: {len(train_labels)} 个")
    print(f"   验证集图片: {len(val_images)} 张")
    print(f"   验证集标注: {len(val_labels)} 个")
    print()
    
    # 检查图片和标注是否一一对应
    errors = []
    
    # 检查训练集
    for img_file in train_images:
        label_file = (dataset_dir / "labels" / "train") / (img_file.stem + ".txt")
        if not label_file.exists():
            errors.append(f" 缺少标注文件: {label_file}")
        else:
            if not validate_annotation_format(label_file):
                errors.append(f"❌ 标注格式错误: {label_file}")
    
    # 检查验证集
    for img_file in val_images:
        label_file = (dataset_dir / "labels" / "val") / (img_file.stem + ".txt")
        if not label_file.exists():
            errors.append(f"❌ 缺少标注文件: {label_file}")
        else:
            if not validate_annotation_format(label_file):
                errors.append(f"❌ 标注格式错误: {label_file}")
    
    # 输出结果
    if errors:
        print(f"⚠️  发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("✅ 数据集验证通过！可以开始训练")
        return True


def create_sample_annotation():
    """创建示例标注文件，帮助用户理解格式"""
    
    sample_dir = Path("datasets/sample_annotation_example")
    sample_dir.mkdir(exist_ok=True)
    
    # 创建示例图片（一个空白图片）
    sample_image = sample_dir / "example_001.jpg"
    img = Image.new('RGB', (1920, 1080), color='white')
    img.save(sample_image)
    
    # 创建示例标注文件
    sample_label = sample_dir / "example_001.txt"
    with open(sample_label, 'w') as f:
        # 格式: class_id x_center y_center width height
        # 假设在图片中间有一个划痕 (class_id=0)
        f.write("0 0.5 0.5 0.1 0.05\n")  # 划痕
        f.write("1 0.3 0.6 0.08 0.06\n")  # 凹陷
    
    print(f"\n📝 示例标注文件已创建: {sample_label}")
    print("   内容说明:")
    print("   - 第 1 行: class_id=0 (划痕), 位置在图片中心, 宽高分别为图片的 10% 和 5%")
    print("   - 第 2 行: class_id=1 (凹陷), 位置在左侧偏下, 宽高分别为图片的 8% 和 6%")
    print()
    print("📖 类别对照表:")
    print("   0: scratch (划痕)")
    print("   1: dent (凹陷)")
    print("   2: collision (碰撞)")
    print("   3: broken (破损)")


if __name__ == "__main__":
    print("=" * 60)
    print("YOLOv8 车损检测 - 数据集准备工具")
    print("=" * 60)
    print()
    
    # 1. 创建目录结构
    print(" 步骤 1: 创建数据集目录结构")
    print("-" * 60)
    dataset_dir = prepare_dataset_structure()
    print()
    
    # 2. 创建示例标注
    print("📝 步骤 2: 生成示例标注文件")
    print("-" * 60)
    create_sample_annotation()
    
    # 3. 验证数据集（如果已存在数据）
    print("🔍 步骤 3: 验证数据集")
    print("-" * 60)
    if (dataset_dir / "images" / "train").exists():
        validate_dataset(dataset_dir)
    else:
        print("ℹ️  数据集目录为空，请按照以下步骤导入数据:")
        print()
        print("1️⃣  将训练图片放入: datasets/car-damage-dataset/images/train/")
        print("2️  将验证图片放入: datasets/car-damage-dataset/images/val/")
        print("3️⃣  将对应的标注文件(.txt)放入 labels/train/ 和 labels/val/")
        print("4️⃣  标注文件格式: <class_id> <x_center> <y_center> <width> <height>")
        print("5️⃣  运行此脚本进行验证")
        print()
        print("📖 推荐使用标注工具:")
        print("   - LabelImg (图形化标注工具)")
        print("   - CVAT (在线标注平台)")
        print("   - Roboflow (数据集管理平台)")
