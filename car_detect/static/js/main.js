// API配置
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
        
        // 准备表单数据
        const formData = new FormData();
        formData.append('file', file);
        formData.append('vehicle_type', vehicleType);
        
        // 发送请求
        const response = await fetch(`${API_BASE}/models/detect`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.code === 0) {
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

function displayResult(data) {
    const detectionData = data.data;
    
    // 构建结果HTML
    const html = `
        <div class="result-title">🎯 检测结果</div>
        
        <!-- 图片预览与Canvas叠加层 -->
        <div class="image-preview-container" style="position: relative; margin: 20px 0;">
            <img id="resultImage" src="${detectionData.image_url}" alt="检测结果" style="max-width: 100%; border-radius: 10px;">
            <canvas id="damageCanvas" style="position: absolute; top: 0; left: 0; pointer-events: none;"></canvas>
        </div>
        
        <!-- 检测详情卡片 -->
        <div style="margin-top: 20px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="color: #667eea; margin-bottom: 15px;">📊 检测统计</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="padding: 15px; background: #f8f9ff; border-radius: 8px;">
                    <div style="font-size: 0.9em; color: #666;">文件名</div>
                    <div style="font-weight: 600; color: #333; margin-top: 5px;">${detectionData.filename}</div>
                </div>
                <div style="padding: 15px; background: #f8f9ff; border-radius: 8px;">
                    <div style="font-size: 0.9em; color: #666;">检测对象数</div>
                    <div style="font-weight: 600; color: #333; margin-top: 5px;">${detectionData.detections.detection_count}</div>
                </div>
                <div style="padding: 15px; background: #f8f9ff; border-radius: 8px;">
                    <div style="font-size: 0.9em; color: #666;">处理时间</div>
                    <div style="font-weight: 600; color: #333; margin-top: 5px;">${new Date(detectionData.processing_time).toLocaleString()}</div>
                </div>
            </div>
        </div>
        
        <!-- 检测报告 -->
        <div style="margin-top: 20px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h3 style="color: #667eea; margin-bottom: 15px;">📝 AI分析报告</h3>
            <div class="report-content">
                ${formatReport(detectionData.report)}
            </div>
        </div>
        
        <!-- 3D模型跳转按钮 -->
        <div style="text-align: center; margin-top: 20px;">
            <button onclick="window.location.href='/3d-viewer.html'" class="btn btn-secondary" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                🎨 查看3D模型
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
