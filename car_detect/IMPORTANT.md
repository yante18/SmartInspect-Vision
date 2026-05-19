# ⚠️ 重要提示 - 部署前必读

## 🎯 项目状态

✅ **项目已完整创建，所有代码文件已就绪**
✅ **可直接部署到服务器使用**
⚠️ **当前为演示版本，检测结果为模拟数据**

---

## 📋 部署前检查清单

### Windows本地开发

- [ ] 已安装 Python 3.9 或更高版本
- [ ] 已解压项目到任意目录
- [ ] 准备双击运行 `start.bat`

### Linux服务器部署

- [ ] 服务器已安装 Python 3.9+
- [ ] 已上传项目到服务器（建议路径：/opt/car_detect）
- [ ] 已赋予脚本执行权限：`chmod +x deploy.sh`
- [ ] 准备以sudo权限运行：`sudo ./deploy.sh`

---

## 🚀 快速启动（3步完成）

### 方式一：Windows用户

```bash
# 1. 进入项目目录
cd car_detect

# 2. 双击运行启动脚本
start.bat

# 3. 浏览器访问
http://127.0.0.1:8000
```

### 方式二：Linux用户

```bash
# 1. 上传并解压项目
tar -xzf car_detect_v1.0.tar.gz
cd car_detect

# 2. 执行部署脚本
chmod +x deploy.sh
sudo ./deploy.sh

# 3. 浏览器访问
http://YOUR_SERVER_IP:8000
```

---

## 🔧 常见问题速查

### 1️⃣ Python版本过低

**错误信息**: `Python 3.9+ is required`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev

# CentOS
sudo yum install python39 python39-devel
```

### 2️⃣ 端口被占用

**错误信息**: `Address already in use`

**解决方案**:
```bash
# 查看占用端口的进程
lsof -i :8000          # Linux
netstat -ano | findstr :8000  # Windows

# 方法1: 杀死占用进程
kill -9 <PID>

# 方法2: 修改端口
# 编辑 .env 文件，将 PORT=8000 改为其他端口
```

### 3️⃣ 依赖安装失败

**错误信息**: `Could not find a version that satisfies the requirement`

**解决方案**:
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或升级pip
pip install --upgrade pip
```

### 4️⃣ 权限不足（Linux）

**错误信息**: `Permission denied`

**解决方案**:
```bash
# 赋予执行权限
chmod +x deploy.sh
chmod +x package.sh

# 或使用sudo
sudo ./deploy.sh
```

### 5️⃣ 防火墙阻止访问

**现象**: 服务器启动成功但无法访问

**解决方案**:
```bash
# Ubuntu (UFW)
sudo ufw allow 8000/tcp

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

---

## 📝 配置修改指南

### 修改服务器端口

编辑 `.env` 文件：
```env
PORT=8080  # 改为你想要的端口
```

### 修改文件上传大小限制

编辑 `.env` 文件：
```env
MAX_FILE_SIZE=20971520  # 改为20MB（单位：字节）
```

### 修改日志级别

编辑 `.env` 文件：
```env
LOG_LEVEL=DEBUG  # DEBUG/INFO/WARNING/ERROR/CRITICAL
```

---

## 🔍 验证部署成功

### 1. 检查服务状态

```bash
# Linux (systemd)
sudo systemctl status car-detect

# 手动运行
ps aux | grep uvicorn
```

### 2. 测试API接口

```bash
# 健康检查
curl http://localhost:8000/health

# 预期返回:
{"status":"healthy","service":"智检慧眼","version":"1.0.0"}
```

### 3. 访问Web界面

浏览器打开：
- 主页：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 📊 性能优化建议

### 生产环境配置

1. **关闭调试模式**
   ```python
   # main.py 中修改
   uvicorn.run(
       "main:app",
       host="0.0.0.0",
       port=8000,
       reload=False,  # 关闭自动重载
       workers=4      # 多进程
   )
   ```

2. **使用Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

3. **Nginx反向代理**
   - 参考 `nginx.conf.example`
   - 启用静态文件缓存
   - 配置HTTPS

4. **数据库优化**
   - 定期清理旧记录
   - 添加索引
   - 考虑迁移到PostgreSQL

---

## 🔐 安全建议

### 生产环境必做

- [ ] 修改默认端口或使用域名
- [ ] 配置HTTPS证书
- [ ] 限制CORS允许的域名
- [ ] 设置合理的文件大小限制
- [ ] 定期备份数据库
- [ ] 配置防火墙规则
- [ ] 禁用不必要的API接口
- [ ] 添加请求频率限制

### CORS配置修改

编辑 `main.py`：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # 限制具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📞 获取帮助

### 查看日志

```bash
# Linux systemd
sudo journalctl -u car-detect -f

# 查看最新50行
sudo journalctl -u car-detect -n 50

# 查看文件日志
tail -f logs/app_$(date +%Y-%m-%d).log
```

### 重启服务

```bash
sudo systemctl restart car-detect
```

### 停止服务

```bash
sudo systemctl stop car-detect
```

---

## 🎓 学习资源

- **FastAPI官方文档**: https://fastapi.tiangolo.com/
- **Uvicorn文档**: https://www.uvicorn.org/
- **SQLAlchemy文档**: https://docs.sqlalchemy.org/
- **本项目API文档**: http://localhost:8000/docs

---

## ✅ 部署完成检查

部署成功后，您应该能够：

- [ ] 访问 http://YOUR_IP:8000 看到主页
- [ ] 上传图片并看到检测结果
- [ ] 访问 http://YOUR_IP:8000/docs 查看API文档
- [ ] 在 `logs/` 目录看到日志文件
- [ ] 在 `data/` 目录看到数据库文件
- [ ] 在 `static/upload/` 目录看到上传的图片

---

**祝您部署顺利！** 🎉

如有问题，请查看详细文档：
- 📖 README.md - 完整项目文档
- 📖 QUICKSTART.md - 快速开始指南
- 📖 DELIVERY.md - 项目交付清单
