# 内网穿透配置指南

本文档介绍如何让云服务器访问本地电脑的 YOLO 推理服务。

---

## 📋 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **frp** | 稳定、可自定义域名、支持TCP/HTTP | 需要自有服务器 | 长期稳定使用 |
| **ngrok** | 简单易用、免费套餐 | 每次重启URL变化、限速 | 快速测试 |
| **Cloudflare Tunnel** | 免费、安全、无需公网IP | 配置稍复杂 | 生产环境推荐 |
| **端口映射** | 最简单、延迟最低 | 需要公网IP、安全风险 | 有固定公网IP |

---

## 🔧 方案一：frp（推荐）

### 1. 准备条件
- 一台有公网 IP 的服务器（您的云服务器即可）
- frp 下载地址：https://github.com/fatedier/frp/releases

### 2. 服务器端配置（frps）

在云服务器上执行：

```bash
# 下载 frp
wget https://github.com/fatedier/frp/releases/download/v0.61.1/frp_0.61.1_linux_amd64.tar.gz
tar -zxvf frp_0.61.1_linux_amd64.tar.gz
cd frp_0.61.1_linux_amd64

# 创建配置文件
cat > frps.ini << EOF
[common]
bind_port = 7000
token = your-frp-token-here
EOF

# 启动 frps
./frps -c frps.ini
```

### 3. 本地客户端配置（frpc）

在本地电脑执行：

```powershell
# 下载 Windows 版 frp
# 从 https://github.com/fatedier/frp/releases 下载 frp_0.61.1_windows_amd64.zip
# 解压到 C:\frp

# 创建配置文件 frpc.ini
[common]
server_addr = YOUR_SERVER_IP
server_port = 7000
token = your-frp-token-here

[yolo_service]
type = tcp
local_ip = 127.0.0.1
local_port = 9000
remote_port = 9000
```

```powershell
# 启动 frpc
cd C:\frp
.\frpc.exe -c frpc.ini
```

### 4. 更新云端配置

修改 `.env` 文件：

```env
REMOTE_YOLO_URL=http://YOUR_SERVER_IP:9000
YOLO_API_TOKEN=your-secret-token-here
USE_REMOTE_YOLO=true
```

---

## 🔧 方案二：ngrok（快速测试）

### 1. 注册 ngrok
访问 https://ngrok.com 注册账号，获取 Authtoken

### 2. 安装 ngrok

```powershell
# 下载 ngrok
# https://ngrok.com/download

# 配置 token
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 3. 启动隧道

```powershell
# 暴露本地 9000 端口
ngrok http 9000
```

ngrok 会生成一个临时 URL，如：`https://abc123.ngrok.io`

### 4. 更新云端配置

```env
REMOTE_YOLO_URL=https://abc123.ngrok.io
YOLO_API_TOKEN=your-secret-token-here
USE_REMOTE_YOLO=true
```

---

## 🔧 方案三：Cloudflare Tunnel（生产推荐）

### 1. 安装 cloudflared

```powershell
# Windows 下载
# https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe

# 移动到系统路径
Move-Item cloudflared-windows-amd64.exe C:\Windows\System32\cloudflared.exe
```

### 2. 登录 Cloudflare

```powershell
cloudflared tunnel login
```

浏览器会打开 Cloudflare 登录页面，选择您的域名。

### 3. 创建隧道

```powershell
# 创建隧道
cloudflared tunnel create yolo-tunnel

# 记录 Tunnel ID 和 credentials.json 路径
```

### 4. 配置路由

创建 `config.yml`：

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: C:\Users\YourName\.cloudflared\YOUR_TUNNEL_ID.json

ingress:
  - hostname: yolo.your-domain.com
    service: http://localhost:9000
  - service: http_status:404
```

### 5. 启动隧道

```powershell
cloudflared tunnel run --config config.yml yolo-tunnel
```

### 6. DNS 配置

在 Cloudflare Dashboard 添加 CNAME 记录：
- 名称：`yolo`
- 目标：`YOUR_TUNNEL_ID.cfargotunnel.com`

### 7. 更新云端配置

```env
REMOTE_YOLO_URL=https://yolo.your-domain.com
YOLO_API_TOKEN=your-secret-token-here
USE_REMOTE_YOLO=true
```

---

## 🔧 方案四：路由器端口映射（最简单）

### 1. 获取本地电脑内网 IP

```powershell
ipconfig
# 记录 IPv4 地址，如 192.168.1.100
```

### 2. 配置路由器端口转发

登录路由器管理页面（通常 192.168.1.1）：
- 找到"端口转发"或"虚拟服务器"
- 添加规则：
  - 外部端口：9000
  - 内部 IP：192.168.1.100
  - 内部端口：9000
  - 协议：TCP

### 3. 获取公网 IP

访问 https://ip.cn 查看您的公网 IP

### 4. 更新云端配置

```env
REMOTE_YOLO_URL=http://YOUR_PUBLIC_IP:9000
YOLO_API_TOKEN=your-secret-token-here
USE_REMOTE_YOLO=true
```

⚠️ **注意**：大多数家庭宽带没有固定公网 IP，重启路由器后 IP 会变化。

---

## 🔒 安全性配置

### 1. API Token 认证

所有方案都已集成 Token 认证，确保设置强密码：

```env
YOLO_API_TOKEN=complex-random-string-here-12345
```

### 2. HTTPS 加密

- **frp**: 配置 SSL 证书
- **ngrok**: 自动提供 HTTPS
- **Cloudflare**: 自动 HTTPS
- **端口映射**: 需自行配置 Nginx + Let's Encrypt

### 3. IP 白名单（可选）

在 `local_yolo_service.py` 中添加：

```python
from fastapi import Request

ALLOWED_IPS = ["YOUR_SERVER_IP"]

@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    response = await call_next(request)
    return response
```

---

## ⚡ 性能优化

### 1. 图片压缩

在上传前压缩图片以减少传输时间：

```python
from PIL import Image
import io

def compress_image(image_path, max_size=1024, quality=85):
    img = Image.open(image_path)
    
    # 调整尺寸
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    
    # 保存为 JPEG
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)
    
    return buffer
```

### 2. 异步请求

使用 `aiohttp` 替代 `requests` 实现异步调用：

```python
import aiohttp

async def detect_async(image_path: str):
    async with aiohttp.ClientSession() as session:
        with open(image_path, "rb") as f:
            data = aiohttp.FormData()
            data.add_field("file", f, filename=Path(image_path).name)
            
            async with session.post(
                f"{self.base_url}/detect",
                data=data,
                headers={"X-API-Token": self.api_token}
            ) as response:
                return await response.json()
```

### 3. 连接池复用

```python
# 在 RemoteYOLOClient 中复用 session
self.session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,
    pool_maxsize=20,
    max_retries=3
)
self.session.mount('http://', adapter)
self.session.mount('https://', adapter)
```

---

## 🧪 测试连接

### 1. 本地服务测试

```powershell
# 启动本地服务
python local_yolo_service.py

# 健康检查
curl http://localhost:9000/health

# 测试检测
curl -X POST http://localhost:9000/detect \
  -H "X-API-Token: your-secret-token-here" \
  -F "file=@test.jpg"
```

### 2. 云端测试

在云服务器上执行：

```bash
# 测试远程连接
curl -X POST http://YOUR_SERVER_IP:9000/health

# 测试检测
curl -X POST http://YOUR_SERVER_IP:9000/detect \
  -H "X-API-Token: your-secret-token-here" \
  -F "file=@test.jpg"
```

### 3. 完整流程测试

```bash
# 重启云端服务
ssh yan "cd /opt/car-detect && docker compose restart"

# 查看日志
ssh yan "docker logs -f car-detect-app"

# 应该看到：
# [ModelRouter] 使用远程 YOLO 服务
# [RemoteYOLO] 初始化远程客户端: http://YOUR_SERVER_IP:9000
```

---

## 📊 监控与日志

### 1. 添加请求日志

在 `local_yolo_service.py` 中添加中间件：

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        log.info(
            f"[Request] {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Duration: {duration:.2f}s"
        )
        
        return response

app.add_middleware(LoggingMiddleware)
```

### 2. Prometheus 监控（可选）

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

访问 `http://localhost:9000/metrics` 查看指标。

---

## ❓ 常见问题

### Q1: 连接超时怎么办？
- 检查防火墙是否开放端口
- 确认 frp/ngrok 隧道正常运行
- 增加 timeout 参数

### Q2: 检测速度慢？
- 检查网络带宽
- 压缩上传图片
- 考虑使用 GPU 加速

### Q3: Token 验证失败？
- 确认两端 Token 一致
- 检查 Header 名称是否为 `X-API-Token`

### Q4: 如何开机自启本地服务？

创建 Windows 任务计划程序或使用 PM2：

```powershell
# 使用 NSSM 创建 Windows 服务
nssm install YOLOService python C:\path\to\local_yolo_service.py
nssm start YOLOService
```

---

**最后更新：** 2026-05-21
