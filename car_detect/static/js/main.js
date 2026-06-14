// 演示模式配置 - 设置为 false 使用真实后端
const DEMO_MODE = false;
const API_BASE = '/api/v1';

// DOM元素
let fileInput, uploadArea, vehicleTypeSelect, submitBtn, resultSection, loadingSection;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initElements();
    initEventListeners();
});

function initElements() {
    fileInput = document.getElementById('fileInput');
    uploadArea = document.getElementById('uploadArea');
    vehicleTypeSelect = document.getElementById('vehicleType');
    submitBtn = document.getElementById('submitBtn');
    resultSection = document.getElementById('resultSection');
    loadingSection = document.getElementById('loadingSection');
}

function initEventListeners() {
    // 点击上传区域
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // 文件选择
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽事件
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // 提交按钮
    submitBtn.addEventListener('click', handleSubmit);
    
    // 3D查看按钮
    const view3DBtn = document.getElementById('view3DBtn');
    if (view3DBtn) {
        view3DBtn.addEventListener('click', () => {
            window.location.href = '/3d-viewer.html';
        });
    }
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect({ target: fileInput });
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
        showNotification('请选择图片文件', 'error');
        return;
    }
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = function(event) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'image-preview';
        previewDiv.innerHTML = `
            <img src="${event.target.result}" alt="预览图片">
            <p style="margin-top: 10px; color: #666;">${file.name}</p>
        `;
        
        // 移除旧预览
        const oldPreview = uploadArea.querySelector('.image-preview');
        if (oldPreview) oldPreview.remove();
        
        uploadArea.appendChild(previewDiv);
    };
    reader.readAsDataURL(file);
}

async function handleSubmit() {
    const file = fileInput.files[0];
    if (!file) {
        showNotification('请先选择图片', 'error');
        return;
    }
    
    const vehicleType = vehicleTypeSelect.value;
    
    try {
        // 显示加载状态
        submitBtn.disabled = true;
        submitBtn.textContent = '检测中...';
        loadingSection.classList.add('show');
        resultSection.classList.remove('show');
        
        let data;
        
        if (DEMO_MODE) {
            // 演示模式：模拟检测结果
            await new Promise(resolve => setTimeout(resolve, 2000)); // 模拟延迟
            data = generateDemoResult(file.name);
        } else {
            // 准备表单数据
            const formData = new FormData();
            formData.append('file', file);
            formData.append('vehicle_type', vehicleType);
            
            // 发送请求到后端
            const response = await fetch(`${API_BASE}/models/detect`, {
                method: 'POST',
                body: formData
            });
            
            data = await response.json();
        }
        
        if (data.code === 0 || DEMO_MODE) {
            displayResult(data);
            showNotification('检测成功！', 'success');
        } else {
            throw new Error(data.msg || '检测失败');
        }
        
    } catch (error) {
        console.error('检测错误:', error);
        showNotification(error.message || '网络错误，请检查服务是否启动', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '开始检测';
        loadingSection.classList.remove('show');
    }
}

function generateDemoResult(filename) {
    // 生成演示用的检测结果
    const vehicleTypes = {
        'sedan': '轿车',
        'suv': 'SUV',
        'truck': '卡车',
        'van': '面包车',
        'other': '其他'
    };
    
    const vehicleType = vehicleTypeSelect.value;
    const vehicleTypeName = vehicleTypes[vehicleType] || '车辆';
    
    return {
        code: 0,
        msg: 'success',
        data: {
            filename: filename,
            report: `# ${vehicleTypeName}检测报告\n\n## 基本信息\n- 车辆类型：${vehicleTypeName}\n- 检测时间：${new Date().toLocaleString()}\n- 文件名：${filename}\n\n## 检测结果\n### 外观状况\n- 车身整体状况良好\n- 未发现明显划痕或凹陷\n- 车漆光泽度正常\n\n### 安全检测\n- 轮胎磨损程度：正常\n- 刹车系统：正常\n- 灯光系统：正常\n\n### 建议\n- 建议定期保养\n- 注意检查轮胎气压\n- 保持车辆清洁\n\n---\n*此为演示报告，实际检测需要连接后端AI服务*`,
            detections: {
                detection_count: Math.floor(Math.random() * 5) + 1
            },
            processing_time: new Date().toISOString()
        }
    };
}

function displayResult(data) {
    const detectionData = data.data;
    
    // 构建结果HTML
    const html = `
        <div class="result-title">🎯 检测结果</div>
        
        <!-- 图片预览与Canvas叠加层 -->
        <div class="image-preview-container" style="position: relative; margin: 20px 0;">
            <img id="resultImage" src="${detectionData.image_url}" alt="检测结果" style="max-width: 100%; border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1);">
            <canvas id="damageCanvas" style="position: absolute; top: 0; left: 0; pointer-events: none;"></canvas>
        </div>
        
        <!-- 检测统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">📁</div>
                <div class="stat-label">${detectionData.filename}</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${detectionData.detections.detection_count}</div>
                <div class="stat-label">检测数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">⏱️</div>
                <div class="stat-label">${new Date(detectionData.processing_time).toLocaleString()}</div>
            </div>
        </div>
        
        <!-- 检测结果列表 -->
        <div style="margin-top: 20px;">
            <h3 style="color: #f8fafc; font-weight: 600; margin-bottom: 15px; font-size: 1.1em;">🔍 损伤检测结果</h3>
            ${detectionData.detections.results && detectionData.detections.results.length > 0 ? 
                detectionData.detections.results.map((dmg, index) => `
                    <div class="detection-card">
                        <div class="type">${dmg.type}</div>
                        <div class="location">📍 ${dmg.location || '未知位置'}</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${Math.round(dmg.confidence * 100)}%"></div>
                        </div>
                        <div style="margin-top: 8px; font-size: 13px; color: #94a3b8;">
                            置信度: ${Math.round(dmg.confidence * 100)}%
                        </div>
                    </div>
                `).join('') : 
                '<div style="padding: 20px; text-align: center; color: #94a3b8; background: rgba(99, 102, 241, 0.1); border-radius: 12px;">未检测到损伤</div>'
            }
        </div>
        
        <!-- 检测报告 -->
        <div style="margin-top: 20px; padding: 25px; background: rgba(0,0,0,0.2); border-radius: 14px; border: 1px solid rgba(255,255,255,0.1);">
            <h3 style="color: #6366f1; margin-bottom: 15px; font-size: 1.2em; font-weight: 600;">📝 AI分析报告</h3>
            <div class="report-content">
                ${formatReport(detectionData.report)}
            </div>
        </div>
        
        <!-- 3D模型跳转按钮 -->
        <div style="text-align: center; margin-top: 25px;">
            <button onclick="window.location.href='/3d-viewer.html'" class="btn btn-secondary">
                🎨 查看3D模型
            </button>
            <button onclick="window.location.href='/damage-viewer.html'" class="btn btn-primary" style="margin-left: 12px;">
                🔍 查看3D损伤
            </button>
        </div>
    `;
    
    resultSection.innerHTML = html;
    resultSection.classList.add('show');
    
    // 绘制检测结果到Canvas
    setTimeout(() => {
        drawDamageOverlay(detectionData.detections.results, 'damageCanvas', detectionData.image_url);
    }, 100);
    
    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Canvas 可视化绘制检测结果
async function drawDamageOverlay(damages, canvasId, imageUrl) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !damages || damages.length === 0) return;
    
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.crossOrigin = "anonymous";
    img.onload = () => {
        // 设置Canvas尺寸与图片一致
        canvas.width = img.width;
        canvas.height = img.height;
        
        // 遍历所有检测结果并绘制
        damages.forEach((dmg, index) => {
            const [x1, y1, x2, y2] = dmg.bbox;
            const width = x2 - x1;
            const height = y2 - y1;
            
            // 绘制边界框
            ctx.strokeStyle = '#ff4d4f';
            ctx.lineWidth = 3;
            ctx.strokeRect(x1, y1, width, height);
            
            // 绘制半透明填充
            ctx.fillStyle = 'rgba(255, 77, 79, 0.15)';
            ctx.fillRect(x1, y1, width, height);
            
            // 绘制标签背景
            const label = `${dmg.type} ${Math.round(dmg.confidence * 100)}%`;
            ctx.font = 'bold 14px Arial';
            const textWidth = ctx.measureText(label).width;
            
            ctx.fillStyle = '#ff4d4f';
            ctx.fillRect(x1, y1 - 25, textWidth + 10, 25);
            
            // 绘制标签文字
            ctx.fillStyle = '#fff';
            ctx.fillText(label, x1 + 5, y1 - 7);
            
            // 绘制位置信息
            const locationLabel = dmg.location || '';
            if (locationLabel) {
                ctx.font = '12px Arial';
                const locWidth = ctx.measureText(locationLabel).width;
                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.fillRect(x1, y2, locWidth + 8, 18);
                ctx.fillStyle = '#fff';
                ctx.fillText(locationLabel, x1 + 4, y2 + 13);
            }
        });
        
        console.log(`[Canvas] 已绘制 ${damages.length} 个检测结果`);
    };
    
    img.onerror = (err) => {
        console.error('[Canvas] 图片加载失败:', err);
    };
    
    img.src = imageUrl;
}

function formatReport(report) {
    // 将Markdown格式转换为HTML
    return report
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/\n/g, '<br>');
}

function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    `;
    
    // 设置颜色
    if (type === 'success') {
        notification.style.background = 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)';
    } else if (type === 'error') {
        notification.style.background = 'linear-gradient(135deg, #eb3349 0%, #f45c43 100%)';
    } else {
        notification.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 添加动画样式
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// 按钮波纹点击特效
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function(e) {
                const rect = button.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                const x = e.clientX - rect.left - size / 2;
                const y = e.clientY - rect.top - size / 2;
                
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                ripple.style.cssText = `
                    position: absolute;
                    width: ${size}px;
                    height: ${size}px;
                    left: ${x}px;
                    top: ${y}px;
                    background: rgba(255, 255, 255, 0.5);
                    border-radius: 50%;
                    transform: scale(0);
                    animation: rippleEffect 0.6s linear;
                    pointer-events: none;
                `;
                
                button.style.position = 'relative';
                button.style.overflow = 'hidden';
                button.appendChild(ripple);
                
                setTimeout(() => ripple.remove(), 600);
            });
        });
    }, 100);
});

// 添加波纹动画样式
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes rippleEffect {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);
