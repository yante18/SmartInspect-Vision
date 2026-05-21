# YOLOv8 车损检测 - 训练指南

## 📋 目录

1. [环境准备](#环境准备)
2. [数据准备](#数据准备)
3. [模型训练](#模型训练)
4. [模型使用](#模型使用)
5. [常见问题](#常见问题)

---

## 🛠️ 环境准备

### 1. 激活虚拟环境

```bash
cd c:\Users\Administrator\Desktop\服务器\SmartInspect-Vision\car_detect
.\venv\Scripts\activate
```

### 2. 确认依赖已安装

```bash
pip list | Select-String "ultralytics|opencv|torch"
```

应显示：
- ultralytics >= 8.0.0
- opencv-python >= 4.8.0
- torch >= 2.0.0
- torchvision >= 0.15.0

---

## 📦 数据准备

### 1. 创建数据集目录结构

运行以下命令创建标准的数据集目录：

```bash
python prepare_dataset.py
```

这将创建以下结构：

```
datasets/car-damage-dataset/
├── images/
│   ├── train/          # 训练集图片（JPG/PNG）
│   └── val/            # 验证集图片（JPG/PNG）
├── labels/
│   ├── train/          # 训练集标注文件（.txt）
│   └── val/            # 验证集标注文件（.txt）
└── car_damage.yaml     # 数据集配置文件
```

### 2. 准备标注数据

#### 方式一：使用标注工具

推荐使用以下工具进行标注：

1. **LabelImg**（推荐）
   ```bash
   pip install labelimg
   labelimg
   ```
   - 打开软件，设置输出格式为 **YOLO**
   - 标注类别：scratch, dent, collision, broken
   - 保存后会自动生成 `.txt` 标注文件

2. **CVAT**（在线标注）
   - 访问 https://cvat.ai/
   - 创建项目，上传数据集
   - 选择 YOLO 格式导出标注

3. **Roboflow**（一站式平台）
   - 访问 https://roboflow.com/
   - 上传数据集
   - 在线标注后导出 YOLO 格式

#### 方式二：手动创建标注

每个图片对应一个同名 `.txt` 文件，格式如下：

```
<class_id> <x_center_norm> <y_center_norm> <width_norm> <height_norm>
```

**示例** (假设图片大小为 1920x1080)：
```
0 0.5000 0.5000 0.1000 0.0500
```

这表示：
- 类别 ID = 0（划痕）
- 目标中心在图片的 (50%, 50%) 位置
- 目标宽度为图片的 10%，高度为 5%

#### 类别对照表

| ID | 类别 | 说明 |
|----|------|------|
| 0 | scratch | 划痕 |
| 1 | dent | 凹陷 |
| 2 | collision | 碰撞 |
| 3 | broken | 破损 |

### 3. 验证数据集

标注完成后，运行验证脚本：

```bash
python prepare_dataset.py
```

脚本会自动：
- ✅ 检查所有图片和标注是否一一对应
- ✅ 验证标注格式是否正确
- ✅ 统计数据集数量
- ✅ 提示错误信息

### 4. 数据量建议

| 场景 | 训练集 | 验证集 | 建议 |
|------|--------|--------|------|
| 快速测试 | 50+ | 10+ | 验证流程 |
| 基础模型 | 200+ | 50+ | 可用精度 |
| 生产环境 | 1000+ | 200+ | 高精度 |

---

## 🚀 模型训练

### 1. 基本训练

```bash
python train_yolo.py
```

默认参数：
- epochs: 100（训练轮数）
- batch: 16（批次大小）
- imgsz: 640（图片尺寸）
- device: 0（GPU）

### 2. 自定义参数训练

```bash
# 使用 CPU 训练（较慢但可用）
python train_yolo.py --device cpu

# 减少批次大小（如果显存不足）
python train_yolo.py --batch 8

# 增加训练轮数
python train_yolo.py --epochs 200

# 使用更大的图片尺寸
python train_yolo.py --imgsz 1280
```

### 3. 训练过程监控

训练过程中会：
- 📊 显示实时训练进度
- 📈 生成训练曲线图（runs/detect/car_damage_v1/results.png）
- 💾 保存最佳模型（runs/detect/car_damage_v1/weights/best.pt）

### 4. 训练输出

训练完成后：

```
✅ 训练完成！最佳模型已保存到: car_damage_best.pt
 详细训练日志: runs/detect/car_damage_v1/
📈 mAP@0.5: 0.8523
 mAP@0.5-0.95: 0.6234
```

---

## 🎯 模型使用

### 1. 使用训练好的模型

修改 `models/yolo_engine.py`，将模型路径改为训练后的模型：

```python
# 修改前
self.model_name = "yolov8n.pt"

# 修改后
self.model_name = "car_damage_best.pt"
```

### 2. 测试训练好的模型

```bash
# 测试单张图片
python -c "from ultralytics import YOLO; model = YOLO('car_damage_best.pt'); model.predict('test.jpg', show=True)"

# 测试整个验证集
python -c "from ultralytics import YOLO; model = YOLO('car_damage_best.pt'); metrics = model.val(); print(f'mAP: {metrics.box.map:.4f}')"
```

### 3. 在 Web 应用中使用

重启服务即可使用新模型：

```bash
# 停止当前服务（Ctrl+C）
# 重新启动
python main.py
```

---

## 🔧 常见问题

### Q1: 显存不足怎么办？

```bash
# 减少批次大小
python train_yolo.py --batch 4

# 使用更小的模型
# 下载 yolov8n.pt (nano) 而不是 yolov8s.pt (small)

# 启用混合精度训练（默认已启用）
# amp=True 已在 train_yolo.py 中设置
```

### Q2: 训练很慢怎么办？

1. **使用 GPU**
   - 确保安装了 CUDA 版本的 PyTorch
   - `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118`

2. **使用数据缓存**
   - 已默认启用 `cache="ram"`

3. **减少 workers**
   ```bash
   # 在 train_yolo.py 中修改
   workers=2  # 如果内存不足
   ```

### Q3: 训练后精度不高？

1. **增加数据量**
   - 收集更多标注数据
   - 使用数据增强（已默认启用）

2. **调整学习率**
   ```python
   # 在 train_yolo.py 中调整
   lr0=0.001  # 降低初始学习率
   ```

3. **训练更长时间**
   ```bash
   python train_yolo.py --epochs 200
   ```

4. **检查标注质量**
   - 确保标注框准确
   - 类别标签正确
   - 没有漏标

### Q4: 如何评估模型性能？

```bash
# 运行验证
python -c "
from ultralytics import YOLO
model = YOLO('car_damage_best.pt')
metrics = model.val()
print(f'mAP@0.5: {metrics.box.map50:.4f}')
print(f'mAP@0.5-0.95: {metrics.box.map:.4f}')
print(f'Precision: {metrics.box.mp:.4f}')
print(f'Recall: {metrics.box.mr:.4f}')
"
```

### Q5: 如何可视化训练结果？

训练完成后，查看以下文件：

- `runs/detect/car_damage_v1/results.png` - 训练曲线
- `runs/detect/car_damage_v1/confusion_matrix.png` - 混淆矩阵
- `runs/detect/car_damage_v1/val_batch0_pred.jpg` - 预测结果示例

### Q6: 如何使用不同的 YOLO 模型？

```bash
# 使用 YOLOv8s (small)
python -c "from ultralytics import YOLO; model = YOLO('yolov8s.pt'); model.train(data='car_damage.yaml', epochs=100)"

# 使用 YOLOv8m (medium)
python -c "from ultralytics import YOLO; model = YOLO('yolov8m.pt'); model.train(data='car_damage.yaml', epochs=100)"

# 使用 YOLOv8l (large) - 需要更多显存
python -c "from ultralytics import YOLO; model = YOLO('yolov8l.pt'); model.train(data='car_damage.yaml', epochs=100)"
```

**模型对比：**

| 模型 | 参数量 | 速度 | 精度 | 推荐场景 |
|------|--------|------|------|----------|
| yolov8n | 3.2M | 最快 | 较低 | 快速测试 |
| yolov8s | 11.2M | 快 | 中等 | 平衡 |
| yolov8m | 25.9M | 中等 | 高 | 生产 |
| yolov8l | 43.7M | 慢 | 最高 | 高精度需求 |

---

## 📚 参考资源

- [YOLOv8 官方文档](https://docs.ultralytics.com/)
- [数据集标注教程](https://docs.ultralytics.com/datasets/)
- [模型训练指南](https://docs.ultralytics.com/modes/train/)

---

**快速开始：**

```bash
# 1. 激活环境
.\venv\Scripts\activate

# 2. 准备数据集
python prepare_dataset.py

# 3. 导入标注好的图片和标签到 datasets/car-damage-dataset/

# 4. 开始训练
python train_yolo.py

# 5. 使用训练好的模型
# 修改 models/yolo_engine.py 中的模型路径为 car_damage_best.pt
```
