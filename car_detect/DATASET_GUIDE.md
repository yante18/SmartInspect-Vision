# 车损检测数据集使用指南

##  快速开始

### 方法一：使用百度网盘数据集（推荐）

#### 1. 下载数据集

打开百度网盘，下载以下数据集：

```
链接: https://pan.baidu.com/s/1zYLg1EOwHB-HTBlxQr4w7A
提取码: yhmd
```

**数据集特点：**
- 1000+ 张真实交通事故车辆图像
- 5 个事故等级类别
- YOLO 标准格式
- 已划分训练集和验证集

**类别说明：**
- Class 0: 无事故
- Class 1: 轻微事故
- Class 2: 中等事故
- Class 3: 严重事故
- Class 4: 车辆完全报废

#### 2. 解压数据

下载完成后，解压到一个临时目录，例如：
```
C:\Users\Administrator\Downloads\dataset
```

#### 3. 导入数据

运行以下命令导入数据集：

```bash
cd c:\Users\Administrator\Desktop\服务器\SmartInspect-Vision\car_detect
python import_dataset.py -s "C:\Users\Administrator\Downloads\dataset"
```

**注意：** 将路径替换为你实际解压数据集的位置。

#### 4. 验证数据

```bash
python prepare_dataset.py
```

#### 5. 开始训练

```bash
python train_yolo.py
```

---

### 方法二：从其他来源下载

#### 可用的公开数据集

| 数据集名称 | 图片数量 | 类别数 | 下载链接 |
|-----------|---------|-------|---------|
| CarDD 数据集 | 4000 | 6 | GitHub 搜索 "CarDD dataset" |
| VEHIDE 数据集 | 13945 | 多种 | https://arxiv.org/abs/2303.03185 |
| 交通事故数据集 | 1000+ | 5 | 百度网盘（如上） |

#### 下载后导入

无论从哪里下载，都使用相同的导入方法：

```bash
python import_dataset.py -s "你的数据集路径"
```

---

##  手动下载和使用

### 步骤详解

#### 步骤 1：选择数据集

**选项 A - 百度网盘（最简单）**
- 下载链接：https://pan.baidu.com/s/1zYLg1EOwHB-HTBlxQr4w7A
- 提取码：yhmd
- 大小：约 200-500MB

**选项 B - GitHub 数据集**
```bash
# 克隆 CarDD 数据集
git clone https://github.com/xxx/CarDD-dataset.git
```

**选项 C - Hugging Face**
```
访问：https://huggingface.co/datasets
搜索：car damage detection
```

#### 步骤 2：下载并解压

Windows 解压方法：
1. 右键点击 ZIP 文件
2. 选择 "解压到当前文件夹" 或 "解压到..."
3. 选择一个容易记住的路径

#### 步骤 3：导入到项目

```powershell
# 激活虚拟环境
cd c:\Users\Administrator\Desktop\服务器\SmartInspect-Vision\car_detect
.\venv\Scripts\activate

# 导入数据集
python import_dataset.py -s "C:\Users\你的用户名\Downloads\数据集文件夹名"
```

**实际示例：**
```powershell
python import_dataset.py -s "C:\Users\Administrator\Downloads\交通事故车辆受损数据集"
```

#### 步骤 4：检查导入结果

导入完成后，你应该看到类似这样的输出：

```
============================================================
 导入车损检测数据集
============================================================
 源路径: C:\Users\Administrator\Downloads\交通事故车辆受损数据集
 目标路径: datasets\car-damage-dataset

 找到 1024 张图片
 训练集: 819 张
 验证集: 205 张
 找到 1024 个标注文件

 已复制 2048 个文件

 数据集统计:
   训练集图片: 819 张
   训练集标注: 819 个
   验证集图片: 205 张
   验证集标注: 205 个

 验证通过！可以开始训练
```

#### 步骤 5：开始训练

```bash
# 基本训练
python train_yolo.py

# 自定义参数训练
python train_yolo.py --epochs 100 --batch 16
```

---

##  常见问题

### Q1: 下载失败怎么办？

**解决方案：**
1. 检查网络连接
2. 百度网盘可能需要登录
3. 尝试其他数据集来源（见上方表格）

### Q2: 导入时报错怎么办？

**常见错误和解决方法：**

**错误：源路径不存在**
```
 检查路径是否正确
 确保已经解压了数据集
```

**错误：未找到标注文件**
```
 可能需要手动标注
 安装 labelimg: pip install labelimg
 使用 labelimg 标注图片
```

### Q3: 训练时显存不足怎么办？

```bash
# 减少批次大小
python train_yolo.py --batch 8

# 或使用更小的模型
python train_yolo.py --batch 4
```

### Q4: 如何查看导入的数据？

```bash
# 查看数据集结构
python prepare_dataset.py

# 或直接查看目录
dir datasets\car-damage-dataset
```

---

##  数据集结构说明

成功导入后，数据集结构应该如下：

```
datasets/car-damage-dataset/
├── images/
│   ├── train/          # 训练集图片（80%）
│   └── val/            # 验证集图片（20%）
├── labels/
│   ├── train/          # 训练集标注
│   └── val/            # 验证集标注
└── data.yaml           # 数据集配置（如果有）
```

每个标注文件（.txt）的格式：
```
class_id x_center y_center width height
```

示例：
```
0 0.5 0.5 0.1 0.1
```

---

##  下一步

导入数据后：

1. ✅ **验证数据**：运行 `python prepare_dataset.py`
2. ✅ **开始训练**：运行 `python train_yolo.py`
3. ✅ **监控训练**：查看 `runs/detect/car_damage_v1/` 目录
4. ✅ **使用模型**：训练完成后会自动保存为 `car_damage_best.pt`
5. ✅ **更新系统**：修改 `models/yolo_engine.py` 使用新模型

---

##  快速命令参考

```bash
# 1. 激活虚拟环境
.\venv\Scripts\activate

# 2. 导入数据集（替换为你的实际路径）
python import_dataset.py -s "C:\Users\Administrator\Downloads\dataset"

# 3. 验证数据集
python prepare_dataset.py

# 4. 开始训练
python train_yolo.py

# 5. 查看训练结果
dir runs\detect\car_damage_v1

# 6. 使用训练好的模型（修改 yolo_engine.py 后重启）
python main.py
```

---

**需要帮助？**

如果遇到任何问题，可以：
1. 查看 [TRAINING_GUIDE.md](TRAINING_GUIDE.md) 获取详细训练指南
2. 运行 `python prepare_dataset.py` 检查数据格式
3. 查看 `import_dataset.py` 了解导入逻辑
