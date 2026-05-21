# 分布式 YOLO 推理架构 - 快速开始

## 🎯 一句话说明

**让云服务器通过 HTTP 调用本地电脑的 GPU 进行 YOLO 模型推理，无需购买昂贵的 GPU 服务器。**

---

## 📦 文件清单

### 新增文件

| 文件 | 用途 |
|------|------|
| `local_yolo_service.py` | 本地 YOLO 推理服务（FastAPI） |
| `models/remote_yolo_client.py` | 云端远程调用客户端 |
| `start_local_service.bat` | Windows 一键启动脚本 |
| `test_distributed.py` | 分布式架构测试脚本 |
| `.env.example` | 环境变量配置模板 |
| `REMOTE_DEPLOYMENT_GUIDE.md` | 内网穿透详细配置指南 |
| `DISTRIBUTED_ARCHITECTURE_GUIDE.md` | 完整使用文档 |

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `config.py` | 添加远程服务配置项 |
| `models/model_router.py` | 支持本地/远程模式切换 |
| `requirements.txt` | 添加 requests 依赖 |

---

## 🚀 5 分钟快速上手

### 第 1 步：启动本地服务

```powershell
cd c:\Users\Administrator\Desktop\服务器\SmartInspect-Vision\car_detect

# 双击运行
start_local_service.bat

# 或命令行运行
python local_yolo_service.py
```

看到以下输出表示成功：
```
🚀 启动本地 YOLO 推理服务
📍 服务地址: http://0.0.0.0:9000
```

### 第 2 步：测试本地服务

浏览器访问：http://localhost:9000/docs

或运行测试脚本：
```powershell
python test_distributed.py
```

### 第 3 步：配置内网穿透

选择以下任一方案（推荐 frp）：

#### 方案 A：frp（稳定）
参考 [REMOTE_DEPLOYMENT_GUIDE.md](REMOTE_DEPLOYMENT_GUIDE.md)

#### 方案 B：ngrok（快速）
```powershell
ngrok http 9000
# 记录生成的 URL
```

### 第 4 步：配置云端

编辑 `.env` 文件：

```env
USE_REMOTE_YOLO=true
REMOTE_YOLO_URL=http://YOUR_SERVER_IP:9000  # 或 ngrok URL
YOLO_API_TOKEN=your-secret-token-here
```

上传到服务器并重启：
```bash
scp .env yan:/opt/car-detect/.env
ssh yan "cd /opt/car-detect && docker compose restart"
```

### 第 5 步：验证

访问云端网站上传图片，观察检测结果！

---

## 🔑 核心概念

### 1. 两种运行模式

```python
# 模式 1：本地推理（默认）
USE_REMOTE_YOLO=false
# 云服务器直接加载 YOLO 模型

# 模式 2：远程调用
USE_REMOTE_YOLO=true
# 云服务器通过 HTTP 请求本地电脑
```

**无需修改代码，只需改配置！**

### 2. 工作流程

```
用户上传图片
    ↓
云端 FastAPI 接收
    ↓
判断 USE_REMOTE_YOLO
    ├─ false → 本地 YOLO 引擎推理
    └─ true  → HTTP 请求本地服务
                    ↓
              本地电脑 GPU 推理
                    ↓
              返回检测结果
    ↓
云端保存数据库 + 返回前端
```

### 3. 安全机制

- ✅ **Token 认证**：每次请求必须携带 `X-API-Token`
- ✅ **HTTPS 加密**：内网穿透隧道自动加密
- ✅ **IP 白名单**：可选，限制访问来源
- ✅ **速率限制**：可选，防止滥用

---

## 📊 性能对比

| 指标 | 本地推理 | 远程调用（frp） | 远程调用（ngrok） |
|------|---------|----------------|------------------|
| 延迟 | 100-200ms | 200-400ms | 400-600ms |
| GPU 利用 | 云端 CPU | 本地 GPU | 本地 GPU |
| 成本 | 高（GPU 服务器） | 低（普通服务器） | 低（免费） |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## ❓ 常见问题

### Q1: 为什么要用分布式架构？

**答**：GPU 服务器昂贵（每月数百元），而大多数家庭电脑都有独立显卡。通过分布式架构，可以用低成本实现高性能推理。

### Q2: 网络延迟会影响体验吗？

**答**：对于车辆检测场景（非实时视频流），200-400ms 的延迟完全可以接受。用户体验几乎无差别。

### Q3: 如果本地电脑关机怎么办？

**答**：可以设置 `USE_REMOTE_YOLO=false` 切换回云端本地推理（需要云端也有模型），或保持本地电脑常开。

### Q4: 安全性如何保证？

**答**：
1. Token 认证防止未授权访问
2. HTTPS 加密传输数据
3. 可选 IP 白名单限制来源
4. 建议定期更换 Token

---

## 🎓 学习资源

- [完整使用文档](DISTRIBUTED_ARCHITECTURE_GUIDE.md)
- [内网穿透配置指南](REMOTE_DEPLOYMENT_GUIDE.md)
- [YOLO 集成报告](YOLO_INTEGRATION_COMPLETE.md)

---

## 💡 下一步

1. ✅ 启动本地服务
2. ✅ 配置内网穿透
3. ✅ 测试远程连接
4. 🔄 优化性能（图片压缩、连接池）
5. 🔄 添加监控（Prometheus + Grafana）
6. 🔄 实现异步任务队列（Celery）

---

**祝您使用愉快！** 🎉

如有问题，请查看详细文档或提交 Issue。
