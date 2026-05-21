@echo off
chcp 65001 >nul
echo ========================================
echo   本地 YOLO 推理服务启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [1/3] 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install fastapi uvicorn python-multipart requests pillow ultralytics opencv-python numpy
) else (
    echo [成功] 依赖已安装
)

echo.
echo [2/3] 加载配置...
if not exist .env (
    echo [警告] 未找到 .env 文件，使用默认配置
    echo [提示] 建议复制 .env.example 为 .env 并修改配置
) else (
    echo [成功] 配置文件已加载
)

echo.
echo [3/3] 启动服务...
echo.

REM 设置环境变量（如果 .env 存在）
for /f "tokens=1,2 delims==" %%a in (.env) do (
    set %%a=%%b
)

REM 启动服务
python local_yolo_service.py

pause
