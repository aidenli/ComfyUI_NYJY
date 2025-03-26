from .api import AIModelBridgeFactory
from .definition import *
from PIL import Image
import numpy as np
import base64
import io
import traceback
import hashlib
import json


class ModelOptionBase:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        required = {}
        for modelname in cls.MODEL_LIST:
            required[modelname] = ("BOOLEAN", {"default": False},)
        return {
            "required": required,
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("model",)
    FUNCTION = "run"
    CATEGORY = "NYJY/llm"

    def run(self, **kwargs):
        for k, v in kwargs.items():
            if v:
                return (k,)
        return ("",)


class BailianChatOption(ModelOptionBase):
    MODEL_LIST = bailian_chat_models


class BailianVLOption(ModelOptionBase):
    MODEL_LIST = bailian_vl_models


class BailianI2VOption(ModelOptionBase):
    MODEL_LIST = bailian_i2v_models


class BailianChatNode:
    platform = "bailian"
    cache = {}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "qwen-plus"}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1}),
                "api_key": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2147483647}),
                "history": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Answer",)
    FUNCTION = "chat"
    CATEGORY = "NYJY/llm"
#     DESCRIPTION = """
# 获取阿里百炼API地址：https://bailian.console.aliyun.com/?apiKey=1
# 阿里百炼大模型列表：https://bailian.console.aliyun.com/#/model-market
# """

    def chat(self, model, prompt, max_tokens, api_key, seed, history):
        md5 = hashlib.md5((f"{model}{prompt}{max_tokens}{api_key}{seed}{history}").encode('utf-8')).hexdigest()
        if md5 in self.cache:
            return (self.cache[md5],)

        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})

            if len(history) > 0:
                history_messages = json.loads(history)
            else:
                history_messages = []

            response = model_instance.chat_completion(
                model=model,
                messages=history_messages + [{"role": "user", "content": prompt}],
                max_tokens=int(max_tokens),
                seed=int(seed))
            self.cache[md5] = response
            return (response,)
        except Exception as e:
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            return (str(e), )


class BailianVLNode:
    platform = "bailian"
    cache = {}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "qwen2.5-vl-72b-instruct"}),
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": "请描述这张图片"}),
            },
            "optional": {
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1}),
                "api_key": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2147483647}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("answer",)
    FUNCTION = "chat"
    CATEGORY = "NYJY/llm"
#     DESCRIPTION = """
# 获取阿里百炼API地址：https://bailian.console.aliyun.com/?apiKey=1
# 阿里百炼大模型列表：https://bailian.console.aliyun.com/#/model-market
# """

    def chat(self, model, image, prompt, max_tokens, api_key, seed):
        try:
            if image is None:
                raise ValueError("请上传图片")

            md5 = hashlib.md5((f"{model}{image}{prompt}{max_tokens}{api_key}{seed}").encode('utf-8')).hexdigest()
            if md5 in self.cache:
                return (self.cache[md5],)

            # Convert seed to integer or use None if it's 0
            seed_value = int(seed) if seed != 0 else None

            i = 255.0 * image[0].cpu().numpy()
            input_image = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # 将图片转换为字节流
            image_type = 'png'  # 使用 PNG 格式保存
            buffer = io.BytesIO()
            input_image.save(buffer, format=image_type)
            buffer.seek(0)

            # 转成base64
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})
            response = model_instance.chat_completion(
                model=model,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_type};base64,{base64_image}"},
                    }, {
                        "type": "text", "text": prompt
                    }]
                }],
                max_tokens=int(max_tokens),
                seed=seed_value)  # Use the processed seed value
            self.cache[md5] = response
            return (response,)
        except Exception as e:
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            return (str(e), )


class BailianI2VNode:
    platform = "bailian"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "wanx2.1-i2v-turbo"}),
                "img_url": ("STRING", {"default": ""}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("answer",)
    FUNCTION = "chat"
    CATEGORY = "NYJY/llm"

    def chat(self, model, image, prompt):
        try:
            i = 255.0 * image[0].cpu().numpy()
            input_image = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # 将图片转换为字节流
            image_type = 'png'  # 使用 PNG 格式保存
            buffer = io.BytesIO()
            input_image.save(buffer, format=image_type)
            buffer.seek(0)

            # 转成base64
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            response = model_instance.chat_completion(
                model=model,
                messages=[{
                    "role": "user",
                    "content": [{
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_type};base64,{base64_image}"},
                    }, {
                        "type": "text", "text": prompt
                    }]
                }])
            return (response,)
        except Exception as e:
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            return (str(e), )


class CommonLLMChatNode:
    platform = "common"
    cache = {}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_url": ("STRING", {"default": ""}),
                "model": ("STRING", {"default": ""}),
                "api_key": ("STRING", {"default": ""}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 8192, "step": 1}),
                "history": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Answer",)
    FUNCTION = "chat"
    CATEGORY = "NYJY/llm"

    def chat(self, base_url, model, api_key, prompt, max_tokens,history):
        md5 = hashlib.md5((f"{model}{prompt}{max_tokens}{history}").encode('utf-8')).hexdigest()
        if md5 in self.cache:
            return (self.cache[md5],)

        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            model_instance.set_config(
                {"api_key": api_key, "base_url": base_url})

            if len(history) > 0:
                history_messages = json.loads(history)
            else:
                history_messages = []

            response = model_instance.chat_completion(
                model=model,
                messages=history_messages + [{"role": "user", "content": prompt}],
                max_tokens=max_tokens),
            self.cache[md5] = response
            return (response,)
        except Exception as e:
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            return (str(e), )
