from typing import Optional
from pydantic import BaseModel
import requests
import json
from datetime import datetime
from config import settings
from utils.logger import log

class ReportRequest(BaseModel):
    """报告生成请求"""
    detection_results: dict
    vehicle_info: Optional[dict] = None
    user_notes: Optional[str] = None

class ReportResponse(BaseModel):
    """报告生成响应"""
    code: int
    msg: str
    data: Optional[dict] = None

def generate_inspection_report(detection_data: dict, vehicle_type: str = "sedan") -> str:
    """
    生成车辆检测报告（支持 LLM 增强）
    :param detection_data: 检测数据
    :param vehicle_type: 车辆类型
    :return: 生成的报告文本
    
    优先尝试使用 LM Studio LLM 生成报告，如果失败则回退到模板方式
    """
    # 尝试使用 LLM 生成报告
    if settings.ENABLE_LLM_REPORT:
        try:
            log.info("[LLM] 尝试使用 LLM 生成报告...")
            llm_prompt = build_llm_prompt(detection_data, vehicle_type)
            llm_report = call_lm_studio(llm_prompt)
            
            if llm_report:
                log.info("[LLM] ✅ LLM 报告生成成功")
                return llm_report
            else:
                log.warning("[LLM] ⚠️ LLM 返回为空，回退到模板生成")
        except Exception as e:
            log.error(f"[LLM] ❌ LLM 调用异常: {str(e)}，回退到模板生成")
    
    # 回退到模板生成（原有逻辑）
    log.info("[Template] 使用模板生成报告")
    return _generate_template_report(detection_data, vehicle_type)


def _generate_template_report(detection_data: dict, vehicle_type: str = "sedan") -> str:
    """
    使用模板生成车辆检测报告（回退方案）
    :param detection_data: 检测数据
    :param vehicle_type: 车辆类型
    :return: 生成的报告文本
    """
    detections = detection_data.get('detections', [])
    detection_count = len(detections)
    
    # 车辆类型映射
    vehicle_type_map = {
        "sedan": "轿车",
        "suv": "SUV",
        "truck": "卡车",
        "van": "面包车",
        "other": "其他"
    }
    vehicle_type_cn = vehicle_type_map.get(vehicle_type, "轿车")
    
    # 如果没有检测到损伤
    if detection_count == 0:
        return f"""# 车辆智能检测报告

## 基本信息
- **检测时间**: {detection_data.get('upload_time', 'N/A')}
- **车辆类型**: {vehicle_type_cn}

## 检测结果
✅ **未发现明显外观缺陷**

## 车辆状况评估
根据AI视觉分析，您的车辆外观状况良好，未检测到明显的车损或缺陷。

## 保养建议
1. ✅ 定期保养车辆（建议每5000公里或6个月）
2. ✅ 注意轮胎磨损情况（检查胎纹深度）
3. ✅ 检查车灯是否正常工作
4. ✅ 定期检查机油、冷却液等液体
5. ✅ 保持车身清洁，及时清除鸟粪、树胶等

## 安全评分
⭐⭐⭐⭐⭐ (5/5) - 优秀

---
*本报告由智检慧眼AI系统自动生成*
*检测模型: YOLOv8 车损检测模型 v1.0*
        """.strip()
    
    # 有检测到损伤的情况
    # 统计损伤类型和位置
    damage_types = {}
    locations = {}
    total_confidence = 0
    
    for det in detections:
        dtype = det.get('type', '未知')
        location = det.get('location', '未知')
        confidence = det.get('confidence', 0)
        
        damage_types[dtype] = damage_types.get(dtype, 0) + 1
        locations[location] = locations.get(location, 0) + 1
        total_confidence += confidence
    
    avg_confidence = total_confidence / detection_count if detection_count > 0 else 0
    
    # 严重程度评估
    if detection_count >= 5 or avg_confidence > 0.8:
        severity = "严重"
        safety_rating = "⭐⭐ (2/5)"
        urgency = "🔴 需紧急处理"
    elif detection_count >= 3 or avg_confidence > 0.6:
        severity = "中等"
        safety_rating = "⭐⭐⭐ (3/5)"
        urgency = "🟡 建议近期处理"
    else:
        severity = "轻微"
        safety_rating = "⭐⭐⭐⭐ (4/5)"
        urgency = "🟢 可择期处理"
    
    # 构建损伤详情
    damage_details = "\n".join([
        f"   - **{dtype}**: {count}处" for dtype, count in damage_types.items()
    ])
    
    location_details = "\n".join([
        f"   - **{loc}**: {count}处" for loc, count in locations.items()
    ])
    
    # 维修建议
    repair_suggestions = []
    if any("保险杠" in t for t in damage_types.keys()):
        repair_suggestions.append("• 保险杠损坏需要更换或修复，建议到专业维修店处理")
    if any("车门" in t for t in damage_types.keys()):
        repair_suggestions.append("• 车门凹陷或撕裂需要钣金修复，可能涉及喷漆")
    if any("车灯" in t or "尾灯" in t for t in damage_types.keys()):
        repair_suggestions.append("• 车灯破损影响夜间行驶安全，建议立即更换")
    if any("玻璃" in t or "挡风" in t for t in damage_types.keys()):
        repair_suggestions.append("• 玻璃破损存在安全隐患，建议尽快更换")
    if any("翼子板" in t for t in damage_types.keys()):
        repair_suggestions.append("• 翼子板损伤需要钣金整形和喷漆")
    if any("引擎盖" in t or "后备箱" in t for t in damage_types.keys()):
        repair_suggestions.append("• 引擎盖/后备箱变形可能影响密封性，建议检查并修复")
    if any("车漆" in t or "刮擦" in t for t in damage_types.keys()):
        repair_suggestions.append("• 车漆刮擦可进行抛光或局部补漆处理")
    
    if not repair_suggestions:
        repair_suggestions.append("• 建议到专业维修店进行详细检查和评估")
    
    repair_text = "\n".join(repair_suggestions)
    
    # 估计费用范围
    if detection_count >= 5:
        cost_range = "3000-10000元"
    elif detection_count >= 3:
        cost_range = "1000-3000元"
    else:
        cost_range = "500-1000元"
    
    return f"""# 车辆智能检测报告

## 基本信息
- **检测时间**: {detection_data.get('upload_time', 'N/A')}
- **车辆类型**: {vehicle_type_cn}

## 检测结果
⚠️ **检测到 {detection_count} 处损伤**

### 损伤类型分布
{damage_details}

### 损伤位置分布
{location_details}

### 平均置信度
{avg_confidence:.2%}

## 严重程度评估
- **等级**: {severity}
- **安全评分**: {safety_rating}
- **紧急程度**: {urgency}

## 维修建议
{repair_text}

## 预估费用
💰 **预计维修费用**: {cost_range}

*注：实际费用以维修店报价为准*

## 安全提示
⚠️ **重要提醒**:
1. 如检测到车灯、玻璃等关键部件损坏，请立即处理
2. 结构性损伤（如纵梁、水箱框架）需要专业设备检测
3. 建议保留检测报告用于保险理赔
4. 定期安全检查，确保行车安全

## 后续步骤
1. 📸 保存检测报告和检测图片
2. 🔍 联系保险公司报案（如适用）
3. 🏪 预约专业维修店进行检查
4. 📋 获取详细报价单
5. ✅ 完成维修后进行复检

---
*本报告由智检慧眼AI系统自动生成*
*检测模型: YOLOv8 车损检测模型 v1.0*
*免责声明: 本报告仅供参考，具体维修方案请以专业技师意见为准*
    """.strip()

def create_qwen_prompt(detection_results: dict) -> str:
    """
    创建通义千问Prompt模板（预留）
    :param detection_results: 检测结果
    :return: Prompt文本
    """
    # TODO: 优化Prompt工程
    prompt = f"""
你是一位专业的车辆检测专家。请根据以下检测结果生成专业的检测报告：

检测结果：{detection_results}

请包含以下内容：
1. 车辆整体状况评估
2. 发现的问题及严重程度
3. 维修建议
4. 安全提示

请用专业但易懂的语言撰写报告。
    """
    return prompt


def build_llm_prompt(detection_data: dict, vehicle_type: str = "sedan") -> str:
    """
    构建专业的 LLM Prompt，用于生成车辆损伤检测报告
    :param detection_data: YOLO 检测数据
    :param vehicle_type: 车辆类型
    :return: 格式化的 Prompt 文本
    """
    detections = detection_data.get('detections', [])
    detection_count = len(detections)
    upload_time = detection_data.get('upload_time', datetime.now().isoformat())
    
    # 车辆类型映射
    vehicle_type_map = {
        "sedan": "轿车",
        "suv": "SUV",
        "truck": "卡车",
        "van": "面包车",
        "other": "其他"
    }
    vehicle_type_cn = vehicle_type_map.get(vehicle_type, "轿车")
    
    # 构建详细的损伤信息
    damage_details = []
    for i, det in enumerate(detections, 1):
        damage_info = (
            f"损伤 {i}:\n"
            f"  - 类型: {det.get('type', '未知')}\n"
            f"  - 位置: {det.get('location', '未知')}\n"
            f"  - 置信度: {det.get('confidence', 0):.2%}\n"
            f"  - 边界框: {det.get('bbox', [])}"
        )
        damage_details.append(damage_info)
    
    damage_text = "\n".join(damage_details) if damage_details else "未检测到明显损伤"
    
    # 构建 Prompt
    prompt = f"""# 角色设定
你是一位拥有15年经验的资深车辆定损专家，精通汽车结构、维修工艺和保险理赔流程。

# 任务说明
请根据以下 AI 视觉检测结果，生成一份专业、详细、易懂的车辆损伤检测报告。

# 检测基本信息
- **检测时间**: {upload_time}
- **车辆类型**: {vehicle_type_cn}
- **检测到的损伤数量**: {detection_count} 处

# YOLO 检测结果详情
{damage_text}

# 报告要求
请按照以下结构生成报告，使用 Markdown 格式：

## 1. 车辆整体状况评估
简要描述车辆的整体外观状况，基于检测结果给出总体评价。

## 2. 损伤详细分析
对每一处损伤进行详细说明：
- 损伤的具体位置和类型
- 可能的成因（如碰撞、刮擦等）
- 对车辆安全性和使用的影响
- 损伤的严重程度（轻微/中等/严重）

## 3. 维修方案建议
针对每处损伤提供具体的维修建议：
- 推荐的维修方式（修复/更换）
- 是否需要钣金、喷漆等专业工艺
- 预计的维修工时
- 注意事项

## 4. 费用预估
基于市场行情，给出合理的费用范围：
- 分项费用估算
- 总费用范围
- 说明：实际费用以维修店报价为准

## 5. 安全风险评估
评估当前损伤对行车安全的影响：
- 是否可以继续行驶
- 是否存在安全隐患
- 紧急程度（立即处理/近期处理/可择期处理）

## 6. 保险理赔建议
如适用，提供保险理赔相关建议：
- 是否建议走保险
- 需要保留的证据
- 理赔流程提示

## 7. 后续保养建议
提供车辆日常保养和维护建议。

# 写作风格要求
1. 语言专业但通俗易懂，避免过多技术术语
2. 条理清晰，层次分明
3. 语气客观、中肯
4. 适当使用 emoji 增强可读性（如 ⚠️ 🔧 💰 等）
5. 重要信息加粗强调

# 免责声明
在报告末尾添加：*本报告由 AI 系统辅助生成，仅供参考。具体维修方案请以专业技师现场检测为准。*

请开始生成报告：
"""
    
    return prompt


def call_lm_studio(prompt: str) -> Optional[str]:
    """
    调用本地 LM Studio API 生成报告
    :param prompt: 输入 Prompt
    :return: 生成的报告文本，失败返回 None
    """
    if not settings.ENABLE_LLM_REPORT:
        log.info("[LLM] LLM 报告功能已禁用，使用模板生成")
        return None
    
    try:
        api_url = f"{settings.LM_STUDIO_URL}/chat/completions"
        
        payload = {
            "model": settings.LM_STUDIO_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一位专业的车辆定损专家，擅长生成详细、专业的车辆损伤检测报告。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "stream": False
        }
        
        log.info(f"[LLM] 正在调用 LM Studio: {api_url}")
        log.info(f"[LLM] 模型: {settings.LM_STUDIO_MODEL}")
        
        # 构建请求头
        headers = {"Content-Type": "application/json"}
        if settings.LM_STUDIO_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.LM_STUDIO_API_TOKEN}"
            log.info("[LLM] 使用 API Token 认证")
        
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=settings.LLM_TIMEOUT
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 提取生成的内容
        if "choices" in result and len(result["choices"]) > 0:
            generated_report = result["choices"][0]["message"]["content"]
            log.info(f"[LLM] 报告生成成功，长度: {len(generated_report)} 字符")
            return generated_report
        else:
            log.warning("[LLM] API 响应格式异常")
            return None
            
    except requests.exceptions.ConnectionError:
        log.warning("[LLM] 无法连接到 LM Studio，请确保服务已启动 (http://localhost:1234)")
        return None
    except requests.exceptions.Timeout:
        log.warning(f"[LLM] 请求超时 ({settings.LLM_TIMEOUT}秒)")
        return None
    except Exception as e:
        log.error(f"[LLM] 调用失败: {str(e)}")
        return None
