import argparse
import shutil
from pathlib import Path
import zipfile
import os


def extract_zip_if_needed(source_path):
    """If source is a zip file, extract it first"""
    source = Path(source_path)
    
    if source.suffix.lower() == '.zip':
        print(f"Extracting zip file: {source}")
        extract_dir = source.parent / source.stem
        with zipfile.ZipFile(source, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print(f"Extracted to: {extract_dir}")
        return extract_dir
    
    return source


def find_dataset_root(source):
    """Find the actual dataset root by looking for common dataset structures"""
    
    # Check if current directory has images/labels structure
    if (source / "images").exists() or (source / "labels").exists():
        return source
    
    # Search for subdirectories that might contain the dataset
    for item in source.iterdir():
        if item.is_dir():
            # Check if this subdirectory contains images/labels
            if (item / "images").exists() or (item / "labels").exists():
                return item
            # Recursively search deeper
            found = find_dataset_root(item)
            if found:
                return found
    
    return None


def import_dataset(source_path, target_dir=None):
    """Import car damage dataset to project"""
    
    # Extract zip if needed
    source = extract_zip_if_needed(source_path)
    source = Path(source)
    
    if not source.exists():
        print(f"Source path not exists: {source}")
        return False
    
    # Find actual dataset root
    print("\nSearching for dataset structure...")
    dataset_root = find_dataset_root(source)
    
    if dataset_root:
        print(f"Found dataset root: {dataset_root}")
        source = dataset_root
    else:
        print(f"Using source as-is: {source}")
    
    if target_dir is None:
        target_dir = Path("datasets/car-damage-dataset")
    else:
        target_dir = Path(target_dir)
    
    print("=" * 60)
    print("Import Car Damage Dataset")
    print("=" * 60)
    print(f"\nSource: {source}")
    print(f"Target: {target_dir}")
    
    # Clean target if exists
    if target_dir.exists():
        print(f"\nCleaning target directory...")
        shutil.rmtree(target_dir)
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Show source structure
    print("\nSource structure:")
    for item in source.iterdir():
        if item.is_dir():
            print(f"   [DIR] {item.name}/")
        else:
            print(f"   [FILE] {item.name}")
    
    # Copy data
    print(f"\nCopying dataset...")
    
    # Case 1: Standard YOLO structure
    if (source / "images").exists() and (source / "labels").exists():
        print("Found standard YOLO dataset structure")
        copy_yolo_dataset(source, target_dir)
    
    # Case 2: Nested standard structure
    elif any((source / subdir / "images").exists() and (source / subdir / "labels").exists() 
             for subdir in source.iterdir() if subdir.is_dir()):
        print("Found nested YOLO dataset structure")
        for subdir in source.iterdir():
            if subdir.is_dir() and (subdir / "images").exists() and (subdir / "labels").exists():
                print(f"Found dataset: {subdir.name}")
                copy_yolo_dataset(subdir, target_dir)
                break
    
    # Case 3: Custom structure, need to organize
    else:
        print("Non-standard structure, trying to organize...")
        organize_custom_dataset(source, target_dir)
    
    print("\n" + "=" * 60)
    print("Dataset import completed!")
    print("=" * 60)
    
    # Verify
    print("\nVerifying dataset...")
    verify_dataset(target_dir)
    
    return True


def copy_yolo_dataset(source, target):
    """Copy standard YOLO format dataset"""
    
    for item in source.iterdir():
        if item.is_dir():
            dest = target / item.name
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target / item.name)
    
    file_count = sum(1 for _ in source.rglob('*'))
    print(f"  Copied {file_count} files")


def organize_custom_dataset(source, target):
    """Organize custom format dataset to standard YOLO format"""
    
    print("\nOrganizing dataset structure...")
    
    # Create standard directory structure
    (target / "images" / "train").mkdir(parents=True, exist_ok=True)
    (target / "images" / "val").mkdir(parents=True, exist_ok=True)
    (target / "labels" / "train").mkdir(parents=True, exist_ok=True)
    (target / "labels" / "val").mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    images = []
    
    for ext in image_extensions:
        images.extend(source.rglob(f"*{ext}"))
    
    print(f"\nFound {len(images)} images")
    
    # Split into train and val (80/20)
    import random
    random.shuffle(images)
    
    split_idx = int(len(images) * 0.8)
    train_images = images[:split_idx]
    val_images = images[split_idx:]
    
    # Copy images
    for img in train_images:
        shutil.copy2(img, target / "images" / "train" / img.name)
    
    for img in val_images:
        shutil.copy2(img, target / "images" / "val" / img.name)
    
    print(f"  Train set: {len(train_images)} images")
    print(f"  Val set: {len(val_images)} images")
    
    # Find and copy labels
    labels_found = 0
    for img in images:
        label_file = img.with_suffix('.txt')
        if label_file.exists():
            if img in train_images:
                shutil.copy2(label_file, target / "labels" / "train" / label_file.name)
            else:
                shutil.copy2(label_file, target / "labels" / "val" / label_file.name)
            labels_found += 1
    
    print(f"\nFound {labels_found} label files")
    
    if labels_found == 0:
        print("  Warning: No label files found")
        print("  Tip: Use labelimg tool to annotate images")


def verify_dataset(dataset_dir):
    """Verify dataset integrity"""
    
    print("\nDataset statistics:")
    
    train_images = list((dataset_dir / "images" / "train").glob("*"))
    val_images = list((dataset_dir / "images" / "val").glob("*"))
    train_labels = list((dataset_dir / "labels" / "train").glob("*.txt"))
    val_labels = list((dataset_dir / "labels" / "val").glob("*.txt"))
    
    print(f"   Train images: {len(train_images)}")
    print(f"   Train labels: {len(train_labels)}")
    print(f"   Val images: {len(val_images)}")
    print(f"   Val labels: {len(val_labels)}")
    
    # Check YAML config
    yaml_files = list(dataset_dir.glob("*.yaml")) + list(dataset_dir.glob("*.yml"))
    if yaml_files:
        print(f"\nFound config file: {yaml_files[0].name}")
        
        # Copy as car_damage.yaml
        target_yaml = Path("car_damage.yaml")
        shutil.copy2(yaml_files[0], target_yaml)
        print(f"  Copied to: {target_yaml}")
    else:
        print("\nWarning: No YAML config file found")
        print("  You need to create car_damage.yaml manually")


def main():
    parser = argparse.ArgumentParser(description="Import car damage dataset")
    parser.add_argument("-s", "--source", type=str, required=True, 
                        help="Source dataset path")
    parser.add_argument("-t", "--target", type=str, default=None,
                        help="Target path (default: datasets/car-damage-dataset)")
    
    args = parser.parse_args()
    
    import_dataset(args.source, args.target)


if __name__ == "__main__":
    main()
