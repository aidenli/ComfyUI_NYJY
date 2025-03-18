import os
import requests
import json
from openai import OpenAI
from typing import Dict, Optional, Type
from .definition import get_platform_config
from ..utils import print_log

class AIModelBridgeFactory:
    _instance: Optional['AIModelBridgeFactory'] = None
    _models: Dict[str, 'AIModelBridge'] = {}
    _model_registry: Dict[str, Type['AIModelBridge']] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIModelBridgeFactory, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def register_model(cls, platform: str, model_class: Type['AIModelBridge']):
        cls._model_registry[platform] = model_class
    
    def get_model(self, platform: str) -> 'AIModelBridge':
        if platform not in self._models:
            config = get_platform_config(platform)
            self._models[platform] = self._create_model(platform, config)
        return self._models[platform]
    
    def _create_model(self, platform: str, config: dict) -> 'AIModelBridge':
        model_class = self._model_registry.get(platform)
        if model_class is None:
            raise ValueError(f"不支持的平台: {platform}")
        return model_class(config)

class AIModelBridge:
    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        self._client = None
        self.task_id = ""
    
    @property
    def client(self):
        """获取客户端实例（单例模式）"""
        if self._client is None:
            self._create_client()
        return self._client
    
    def _create_client(self):
        self._client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def set_config(self, config: dict):
        """设置配置信息"""
        self.config.update(config)
        self.api_key = self.config.get("api_key", "")
        self.base_url = self.config.get("base_url", "")
        self._client = None  # 重置客户端实例
    
    def get_config(self) -> dict:
        """获取当前配置信息"""
        return self.config
        
    def chat_completion(self, model: str, messages: list, **kwargs) -> dict:
        try:
            # 使用传入的model参数，而不是硬编码的模型名称
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                **kwargs  # 支持传入其他参数
            )
            
            reasoning_content = ""  # 定义完整思考过程
            answer_content = ""     # 定义完整回复
            is_answering = False   # 判断是否结束思考过程并开始回复
            for chunk in completion:
                if not chunk.choices:
                    print_log("\nUsage:")
                    continue  # 添加 continue，避免不必要的 else 块
                
                delta = chunk.choices[0].delta
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                    print(delta.reasoning_content, end='', flush=True)
                    reasoning_content += delta.reasoning_content
                else:
                    if delta.content and not is_answering:  # 简化条件判断
                        is_answering = True
                    if delta.content:  # 简化条件判断
                        print(delta.content, end='', flush=True)
                        answer_content += delta.content

            # 蒸馏版deepseek的回答内容放到了reasoning_content中，需要特殊处理
            return answer_content if answer_content != "" else reasoning_content
            
        except Exception as e:
            # 错误处理
            raise Exception(f"聊天补全请求失败: {str(e)}")

    def i2v(self, model: str, input: dict, parameters: dict) -> dict:
        raise NotImplementedError("生成视频功能需要子类实现")

# 阿里百炼网关
class BaiLianBridge(AIModelBridge):
    def i2v(self, model: str, input: dict, parameters: dict) -> dict:
        try:
            if not model or not isinstance(input, dict) or not isinstance(parameters, dict):
                raise ValueError("model, input 和 parameters 不能为空")
                
            prompt = input.get("prompt", "")
            img_url = input.get("img_url", "")
            if not prompt or not img_url:
                raise ValueError("prompt 和 img_url 不能为空")
                
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"

            headers = {
                "X-DashScope-Async": "enable",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": model,
                "input": {
                    "prompt": input.get("prompt", ""),
                    "img_url": input.get("img_url", ""),
                },
                "parameters": {
                    "prompt_extend": True
                }
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            # 检查响应状态码
            if response.status_code != 200:
                raise Exception(f"API请求失败: HTTP {response.status_code}")
                
            return response.json()

        except requests.RequestException as e:
            raise Exception(f"网络请求异常: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析异常: {str(e)}")
        except Exception as e:
            raise Exception(f"未知异常: {str(e)}")

# 火山引擎网关
class VolcEngineBridge(AIModelBridge):
    def i2v(self, model: str, input: dict, parameters: dict) -> dict:
        return {}

class CommonBridge(AIModelBridge):
    def i2v(self, model: str, input: dict, parameters: dict) -> dict:
        return {}
# 使用示例
# factory = AIModelBridgeFactory()
# bailian_model = factory.get_model("bailian")
# response = await bailian_model.chat_completion(messages=[...])

# 注册模型
AIModelBridgeFactory.register_model("bailian", BaiLianBridge)
AIModelBridgeFactory.register_model("volcengine", VolcEngineBridge)
AIModelBridgeFactory.register_model("common", CommonBridge)
