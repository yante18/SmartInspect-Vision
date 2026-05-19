@echo off
REM 智检慧眼 - Windows本地开发启动脚本

echo =========================================
echo   智检慧眼 - 车辆智能检测系统
echo =========================================
echo.

REM 检查Python
echo [1/5] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)
echo [成功] Python环境正常
echo.

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo [2/5] 创建虚拟环境...
    python -m venv venv
    echo [成功] 虚拟环境创建完成
) else (
    echo [2/5] 虚拟环境已存在
)
echo.

REM 激活虚拟环境
echo [3/5] 激活虚拟环境...
call venv\Scripts\activate.bat
echo [成功] 虚拟环境已激活
echo.

REM 安装依赖
echo [4/5] 安装依赖包...
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [成功] 依赖安装完成
echo.

REM 创建必要目录
echo [5/5] 初始化项目结构...
if not exist "static\upload" mkdir static\upload
if not exist "data" mkdir data
if not exist "logs" mkdir logs

if not exist ".env" (
    copy .env.example .env
    echo [提示] 已创建.env配置文件，可根据需要修改
)
echo [成功] 项目结构初始化完成
echo.

REM 启动服务
echo =========================================
echo   启动开发服务器...
echo =========================================
echo.
echo 访问地址: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/docs
echo.
echo 按 Ctrl+C 停止服务器
echo.

python main.py

pause
