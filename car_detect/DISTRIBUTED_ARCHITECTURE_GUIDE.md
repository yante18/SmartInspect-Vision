# 分布式 YOLO 推理架构使用指南

## 📖 概述

本方案实现了**本地 GPU 推理 + 云端服务调用**的分布式架构，让云服务器可以利用本地电脑的 GPU 资源进行 YOLO 模型推理。

### 架构优势

✅ **降低成本**：无需购买昂贵的 GPU 云服务器  
✅ **灵活扩展**：可轻松切换本地/远程推理模式  
✅ **性能优化**：利用本地高性能 GPU  
✅ **安全可靠**：Token 认证 + HTTPS 加密  

---

## 🏗️ 架构设计

```
┌─────────────────┐         HTTP Request          ┌──────────────────┐
│                 │  ┌──────────────────────┐     │                  │
│   云服务器       │  │  内网穿透隧道         │     │   本地电脑       │
│   (Cloud)       │  │  (frp/ngrok/CF)      │     │   (Local PC)     │
│                 │  │                      │     │                  │
│  FastAPI App    │──│── POST /detect ──────│────▶│  YOLO Service    │
│                 │  │                      │     │                  │
│  - 接收图片      │  │  - TCP/HTTP 转发     │     │  - 加载 YOLOv8   │
│  - 业务逻辑      │  │  - Token 验证        │     │  - GPU 推理      │
│  - 数据存储      │  │  - HTTPS 加密        │     │  - 返回结果      │
│                 │  │                      │     │                  │
└─────────────────┘  └──────────────────────┘     └──────────────────┘
```

---

## 🚀 快速开始

### 步骤 1：配置本地服务

#### 1.1 准备环境

```powershell
# 确保已安装 Python 3.8+ 和 CUDA（如有 GPU）
python --version
nvidia-smi  # 检查 GPU
```

#### 1.2 安装依赖

```powershell
cd c:\Users\Administrator\Desktop\服务器\SmartInspect-Vision\car_detect

# 安装依赖
pip install fastapi uvicorn python-multipart requests pillow ultralytics opencv-python numpy
```

#### 1.3 配置环境变量

复制 `.env.example` 为 `.env`：

```powershell
copy .env.example .env
```

编辑 `.env` 文件：

```env
# 设置强密码 Token
YOLO_API_TOKEN=my-super-secret-token-123456
```

#### 1.4 启动服务

双击运行 `start_local_service.bat` 或执行：

```powershell
python local_yolo_service.py
```

看到以下输出表示成功：

```
============================================================
🚀 启动本地 YOLO 推理服务
============================================================
📍 服务地址: http://0.0.0.0:9000
🔑 API Token: my-super-secret-token-123456
📖 API 文档: http://localhost:9000/docs
============================================================
```

#### 1.5 测试本地服务

浏览器访问：http://localhost:9000/docs

或使用 curl 测试：

```powershell
# 健康检查
curl http://localhost:9000/health

# 检测测试
curl -X POST http://localhost:9000/detect ^
  -H "X-API-Token: my-super-secret-token-123456" ^
  -F "file=@test.jpg"
```

---

### 步骤 2：配置内网穿透

选择以下任一方案（推荐 frp 或 Cloudflare Tunnel）：

#### 方案 A：frp（稳定可靠）

参考 [REMOTE_DEPLOYMENT_GUIDE.md](REMOTE_DEPLOYMENT_GUIDE.md) 中的 frp 配置章节。

#### 方案 B：ngrok（快速测试）

```powershell
# 启动 ngrok
ngrok http 9000

# 记录生成的 URL，如：https://abc123.ngrok.io
```

#### 方案 C：Cloudflare Tunnel（生产推荐）

参考 [REMOTE_DEPLOYMENT_GUIDE.md](REMOTE_DEPLOYMENT_GUIDE.md) 中的 Cloudflare 配置章节。

---

### 步骤 3：配置云端服务

#### 3.1 上传文件到服务器

```powershell
# 上传修改的文件
scp models/model_router.py yan:/opt/car-detect/models/model_router.py
scp models/remote_yolo_client.py yan:/opt/car-detect/models/remote_yolo_client.py
scp config.py yan:/opt/car-detect/config.py
scp requirements.txt yan:/opt/car-detect/requirements.txt
```

#### 3.2 配置云端环境变量

在服务器上编辑 `/opt/car-detect/.env`：

```env
# 启用远程 YOLO
USE_REMOTE_YOLO=true

# 远程服务地址（根据内网穿透方案填写）
# frp 方案：
REMOTE_YOLO_URL=http://YOUR_SERVER_IP:9000

# ngrok 方案：
# REMOTE_YOLO_URL=https://abc123.ngrok.io

# Cloudflare 方案：
# REMOTE_YOLO_URL=https://yolo.your-domain.com

# API Token（必须与本地服务一致）
YOLO_API_TOKEN=my-super-secret-token-123456

# 超时时间（秒）
REMOTE_YOLO_TIMEOUT=30
```

#### 3.3 更新依赖并重启

```bash
ssh yan

cd /opt/car-detect

# 更新依赖
docker compose up -d --build

# 查看日志
docker logs -f car-detect-app
```

应该看到：

```
[ModelRouter] 使用远程 YOLO 服务
[RemoteYOLO] 初始化远程客户端: http://YOUR_SERVER_IP:9000
```

---

### 步骤 4：验证连接

#### 4.1 健康检查

```bash
# 在云服务器上执行
curl http://YOUR_SERVER_IP:9000/health
```

应返回：

```json
{
  "status": "ok",
  "detector_loaded": true,
  "model_name": "yolov8n.pt"
}
```

#### 4.2 完整流程测试

访问云端网站上传图片，观察：

1. 前端显示检测结果
2. Canvas 绘制边界框
3. 数据库保存记录
4. 本地服务日志显示检测请求

---

## 🔧 配置说明

### 切换本地/远程模式

只需修改 `.env` 中的 `USE_REMOTE_YOLO`：

```env
# 本地推理（默认）
USE_REMOTE_YOLO=false

# 远程调用
USE_REMOTE_YOLO=true
```

无需修改代码，系统自动切换！

### 性能调优

#### 1. 调整超时时间

```env
# 网络较差时增加超时
REMOTE_YOLO_TIMEOUT=60
```

#### 2. 图片压缩

在 `models/model_router.py` 中添加压缩逻辑：

```python
from PIL import Image
import io

def compress_image(file, max_size=1024, quality=85):
    img = Image.open(file.file)
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer
```

#### 3. 连接池优化

在 `models/remote_yolo_client.py` 中：

```python
import requests.adapters

adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)
self.session.mount('http://', adapter)
self.session.mount('https://', adapter)
```

---

## 🔒 安全建议

### 1. 使用强 Token

```python
# 生成随机 Token
import secrets
print(secrets.token_urlsafe(32))
# 输出：abc123XYZ...（复制到 .env）
```

### 2. 启用 HTTPS

- **frp**: 配置 SSL 证书
- **ngrok**: 自动提供 HTTPS
- **Cloudflare**: 自动 HTTPS
- **端口映射**: Nginx + Let's Encrypt

### 3. IP 白名单

在 `local_yolo_service.py` 中添加：

```python
ALLOWED_IPS = ["YOUR_CLOUD_SERVER_IP"]

@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    return await call_next(request)
```

### 4. 速率限制

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/detect")
@limiter.limit("10/minute")  # 每分钟最多 10 次请求
async def detect_vehicle(request: Request, ...):
    ...
```

---

## 📊 监控与维护

### 1. 查看本地服务日志

```powershell
# 实时日志
python local_yolo_service.py

# 或查看 uvicorn 日志
```

### 2. 查看云端日志

```bash
ssh yan
docker logs -f car-detect-app
```

### 3. 性能监控

访问本地服务的 `/metrics` 端点（需配置 Prometheus）：

```
http://localhost:9000/metrics
```

### 4. 开机自启（Windows）

使用 NSSM 创建 Windows 服务：

```powershell
# 下载 NSSM
# https://nssm.cc/download

# 安装服务
nssm install YOLOService
nssm set YOLOService Application python
nssm set YOLOService AppParameters C:\path\to\local_yolo_service.py
nssm set YOLOService AppDirectory C:\path\to\car_detect

# 启动服务
nssm start YOLOService
```

---

## ❓ 常见问题

### Q1: 连接被拒绝？

**原因**：防火墙阻止或隧道未启动

**解决**：
```powershell
# 检查本地服务是否运行
netstat -ano | findstr :9000

# 检查防火墙
netsh advfirewall firewall show rule name=all | findstr 9000

# 添加防火墙规则
netsh advfirewall firewall add rule name="YOLO Service" dir=in action=allow protocol=TCP localport=9000
```

### Q2: Token 验证失败？

**原因**：两端 Token 不一致

**解决**：
```env
# 确认 .env 和本地服务的 Token 完全一致
YOLO_API_TOKEN=my-super-secret-token-123456
```

### Q3: 检测速度慢？

**原因**：网络延迟或图片过大

**解决**：
- 压缩图片（< 1MB）
- 使用有线网络
- 增加 timeout
- 考虑 GPU 加速

### Q4: 如何调试？

**本地调试**：
```powershell
# 启用详细日志
set LOG_LEVEL=DEBUG
python local_yolo_service.py
```

**云端调试**：
```bash
# 查看详细日志
ssh yan
docker logs --tail 100 car-detect-app
```

---

## 📈 性能基准

| 场景 | 延迟 | 吞吐量 | 适用场景 |
|------|------|--------|----------|
| 本地局域网 | 50-100ms | 10 req/s | 开发测试 |
| frp（同地域） | 100-200ms | 5 req/s | 生产环境 |
| ngrok（免费） | 300-500ms | 2 req/s | 快速演示 |
| Cloudflare | 150-300ms | 5 req/s | 全球访问 |

---

## 🎯 下一步优化

1. **异步推理**：使用 Celery + Redis 实现任务队列
2. **批量处理**：支持一次上传多张图片
3. **缓存机制**：相同图片直接返回缓存结果
4. **负载均衡**：多个本地节点轮流处理请求
5. **模型热更新**：无需重启即可切换模型版本

---

**最后更新：** 2026-05-21  
**版本：** v2.0 (分布式架构)
