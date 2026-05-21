"""
自动下载和处理车损检测数据集

数据集来源：
1. Hugging Face 车损数据集
2. 公开可访问的 YOLO 格式数据集

使用方法:
    python download_dataset.py
"""

import os
import shutil
from pathlib import Path
from urllib.request import urlretrieve
import zipfile
import requests


def download_huggingface_dataset():
    """
    从 Hugging Face 下载车损检测数据集
    
    数据集地址: https://huggingface.co/datasets/viktorliuk/car-damage-detection
    """
    print("=" * 60)
    print("📥 开始下载车损检测数据集")
    print("=" * 60)
    
    dataset_url = "https://huggingface.co/datasets/viktorliuk/car-damage-detection/resolve/main/dataset.zip"
    
    # 创建临时下载目录
    download_dir = Path("temp_download")
    download_dir.mkdir(exist_ok=True)
    
    zip_path = download_dir / "car_damage_dataset.zip"
    
    try:
        print("\n 正在下载数据集...")
        print(f" 来源: Hugging Face")
        print(f" 地址: {dataset_url}")
        print("\n 如果下载失败，请手动访问: https://huggingface.co/datasets")
        print(" 搜索 'car damage detection' 下载数据集\n")
        
        # 尝试下载
        response = requests.get(dataset_url, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(" 数据集下载完成！")
            
            # 解压数据集
            print("\n 正在解压数据集...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            print(" 解压完成！")
            
            # 处理数据集
            process_dataset(download_dir)
            return True
        else:
            print(f" 下载失败，HTTP 状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f" 下载出错: {e}")
        print("\n 备选方案：")
        print("1. 手动从 Hugging Face 下载: https://huggingface.co/datasets")
        print("2. 搜索 'car damage detection' 或 'vehicle damage'")
        print("3. 下载后解压到 temp_download/ 目录")
        print("4. 运行: python prepare_dataset.py 验证数据集")
        return False


def process_dataset(download_dir):
    """处理下载的数据集"""
    
    print("\n" + "=" * 60)
    print(" 处理数据集")
    print("=" * 60)
    
    # 查找解压后的数据集
    possible_dirs = [
        download_dir / "car-damage-detection",
        download_dir / "dataset",
        download_dir / "Car Damage Detection",
    ]
    
    dataset_source = None
    for dir_path in possible_dirs:
        if dir_path.exists():
            dataset_source = dir_path
            break
    
    if not dataset_source:
        print("❌ 未找到解压后的数据集")
        print("📁 请检查 temp_download/ 目录")
        return
    
    print(f"✅ 找到数据集: {dataset_source}")
    
    # 查看数据集结构
    print("\n📂 数据集结构:")
    for item in dataset_source.rglob("*"):
        if item.is_file():
            print(f"   {item.relative_to(dataset_source)}")
    
    # 复制数据集到项目目录
    target_dir = Path("datasets/car-damage-dataset")
    
    print(f"\n 正在复制数据集到: {target_dir}")
    
    if dataset_source.exists():
        # 清理旧数据
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        # 复制整个数据集
        shutil.copytree(dataset_source, target_dir)
        print("✅ 数据集复制完成！")
        
        # 检查数据格式
        check_and_convert_format(target_dir)
    else:
        print("❌ 数据集目录不存在")


def check_and_convert_format(dataset_dir):
    """检查并转换数据格式"""
    
    print("\n" + "=" * 60)
    print("🔍 检查数据格式")
    print("=" * 60)
    
    # 检查是否有 data.yaml 或 car_damage.yaml
    yaml_files = list(dataset_dir.glob("*.yaml")) + list(dataset_dir.glob("*.yml"))
    
    if yaml_files:
        print(f"\n✅ 找到配置文件: {yaml_files[0]}")
        
        # 如果有 data.yaml，复制为 car_damage.yaml
        data_yaml = dataset_dir / "data.yaml"
        if data_yaml.exists():
            target_yaml = Path("car_damage.yaml")
            shutil.copy(data_yaml, target_yaml)
            print(f" 已复制到: {target_yaml}")
    else:
        print("\n️  未找到 YAML 配置文件")
        print(" 可能需要手动创建 data.yaml")
    
    # 检查标注格式
    labels_train = dataset_dir / "labels" / "train"
    if labels_train.exists():
        label_files = list(labels_train.glob("*.txt"))
        if label_files:
            print(f"\n✅ 找到 {len(label_files)} 个标注文件")
            
            # 检查第一个标注文件
            with open(label_files[0], 'r') as f:
                first_line = f.readline().strip()
                parts = first_line.split()
                
                print(f"\n📝 标注格式示例:")
                print(f"   {first_line}")
                
                if len(parts) == 5:
                    print("   ✅ YOLO 格式正确")
                    print(f"   - 类别 ID: {parts[0]}")
                    print(f"   - 中心 X: {parts[1]}")
                    print(f"   - 中心 Y: {parts[2]}")
                    print(f"   - 宽度: {parts[3]}")
                    print(f"   - 高度: {parts[4]}")
                else:
                    print(f"   ️  格式可能需要转换（当前 {len(parts)} 个值）")
    
    print("\n" + "=" * 60)
    print("✅ 数据集处理完成！")
    print("=" * 60)
    print("\n📋 下一步:")
    print("   1. 检查数据集: python prepare_dataset.py")
    print("   2. 开始训练: python train_yolo.py")
    print()


def download_kaggle_dataset():
    """
    从 Kaggle 下载数据集
    
    需要先安装 kaggle 库并配置 API token
    """
    print("\n" + "=" * 60)
    print("📥 从 Kaggle 下载数据集")
    print("=" * 60)
    
    print("\n💡 使用 Kaggle 数据集的步骤:")
    print("   1. 注册 Kaggle 账号: https://www.kaggle.com/")
    print("   2. 获取 API Token (账户设置 -> API)")
    print("   3. 安装 kaggle 库: pip install kaggle")
    print("   4. 配置 API token 到 ~/.kaggle/kaggle.json")
    print("   5. 搜索数据集: https://www.kaggle.com/datasets")
    print("      关键词: car damage, vehicle damage")
    print("\n   示例命令:")
    print("      kaggle datasets download -d username/dataset-name")
    print("      kaggle datasets download -d rohitsingh0108/car-damage-detection")
    print()


def clean_temp_files():
    """清理临时文件"""
    temp_dir = Path("temp_download")
    if temp_dir.exists():
        print("\n 清理临时文件...")
        shutil.rmtree(temp_dir)
        print("✅ 清理完成")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚗 车损检测数据集下载工具")
    print("=" * 60)
    print()
    
    while True:
        print("\n请选择下载方式:")
        print("   1. Hugging Face 自动下载")
        print("   2. Kaggle 下载指南")
        print("   3. 检查已下载的数据集")
        print("   4. 清理临时文件")
        print("   0. 退出")
        
        choice = input("\n请输入选项 (0-4): ").strip()
        
        if choice == '1':
            download_huggingface_dataset()
        elif choice == '2':
            download_kaggle_dataset()
        elif choice == '3':
            dataset_dir = Path("datasets/car-damage-dataset")
            if dataset_dir.exists():
                print(f"\n✅ 数据集已存在: {dataset_dir}")
                check_and_convert_format(dataset_dir)
            else:
                print(f"\n❌ 数据集不存在")
        elif choice == '4':
            clean_temp_files()
        elif choice == '0':
            print("\n👋 退出程序")
            break
        else:
            print("\n⚠️  无效选项，请重新输入")


if __name__ == "__main__":
    main()
