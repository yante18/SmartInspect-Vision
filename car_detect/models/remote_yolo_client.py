"""
远程 YOLO 推理客户端
用于云服务器调用本地电脑的 YOLO 服务
"""
import requests
from typing import List, Dict, Optional
from pathlib import Path
import base64
from utils.logger import log
from config import settings

class RemoteYOLOClient:
    """远程 YOLO 推理客户端"""
    
    def __init__(
        self,
        base_url: str = None,
        api_token: str = None,
        timeout: int = 30
    ):
        """
        初始化远程客户端
        :param base_url: 本地服务地址（如 http://your-local-ip:9000）
        :param api_token: API 认证 Token
        :param timeout: 请求超时时间（秒）
        """
        self.base_url = base_url or settings.REMOTE_YOLO_URL
        self.api_token = api_token or settings.YOLO_API_TOKEN
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认 headers
        self.session.headers.update({
            "X-API-Token": self.api_token
        })
        
        log.info(f"[RemoteYOLO] 初始化远程客户端: {self.base_url}")
    
    def health_check(self) -> bool:
        """
        健康检查
        :return: 服务是否可用
        """
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                log.info(f"[RemoteYOLO] 健康检查通过: {data}")
                return True
            else:
                log.error(f"[RemoteYOLO] 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            log.error(f"[RemoteYOLO] 健康检查异常: {e}")
            return False
    
    def detect(self, image_path: str) -> List[Dict]:
        """
        远程调用 YOLO 检测
        :param image_path: 图片路径
        :return: 检测结果列表
        """
        try:
            with open(image_path, "rb") as f:
                files = {"file": (Path(image_path).name, f, "image/jpeg")}
                
                response = self.session.post(
                    f"{self.base_url}/detect",
                    files=files,
                    timeout=self.timeout
                )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"检测失败: {result.get('msg')}")
            
            detections = result.get("data", {}).get("results", [])
            log.info(f"[RemoteYOLO] 检测到 {len(detections)} 个对象")
            
            return detections
        
        except requests.exceptions.Timeout:
            log.error(f"[RemoteYOLO] 请求超时 ({self.timeout}s)")
            raise Exception("远程服务响应超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            log.error(f"[RemoteYOLO] 连接失败: {self.base_url}")
            raise Exception("无法连接到远程 YOLO 服务，请检查服务是否启动")
        except Exception as e:
            log.error(f"[RemoteYOLO] 检测失败: {e}")
            raise
    
    def detect_and_draw(self, image_path: str) -> Dict:
        """
        远程检测并获取标注图片
        :param image_path: 图片路径
        :return: 包含检测结果和标注图片的字典
        """
        try:
            with open(image_path, "rb") as f:
                files = {"file": (Path(image_path).name, f, "image/jpeg")}
                
                response = self.session.post(
                    f"{self.base_url}/detect_and_draw",
                    files=files,
                    timeout=self.timeout
                )
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"处理失败: {result.get('msg')}")
            
            data = result.get("data", {})
            
            # 解码 Base64 图片
            if "annotated_image_base64" in data:
                image_bytes = base64.b64decode(data["annotated_image_base64"])
                output_path = Path(image_path).parent / f"remote_result_{Path(image_path).name}"
                with open(output_path, "wb") as img_file:
                    img_file.write(image_bytes)
                data["annotated_image_path"] = str(output_path)
            
            return data
        
        except Exception as e:
            log.error(f"[RemoteYOLO] 检测绘制失败: {e}")
            raise
    
    def close(self):
        """关闭会话"""
        self.session.close()


# 全局单例
_remote_client = None

def get_remote_client() -> RemoteYOLOClient:
    """获取远程客户端单例"""
    global _remote_client
    if _remote_client is None:
        _remote_client = RemoteYOLOClient()
    return _remote_client
