from .api import AIModelBridgeFactory, ModelOptionBase
from .definition import *
from PIL import Image
import numpy as np
import base64
import io
import json
import torch
import hashlib

class VolcengineChatOption(ModelOptionBase):
    MODEL_LIST = volcengine_chat_models


class VolcengineImageOption(ModelOptionBase):
    MODEL_LIST = volcengine_image_models

class VolcengineChatNode:
    platform = "volcengine"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "doubao-seed-1-6-vision-250815"}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "max_tokens": ("INT", {"default": 4096, "min": 1, "max": 8192, "step": 1}),
                "history": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("Answer",)
    FUNCTION = "chat"
    CATEGORY = "NYJY/Volcengine"

    def chat(self, model, prompt, api_key, max_tokens, history):
        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})

            if len(history) > 0:
                history_messages = json.loads(history)
            else:
                history_messages = []

            # 生成缓存键
            cache_key = hashlib.md5(f"{model}_{prompt}_{history}".encode()).hexdigest()
            
            # 检查缓存
            if cache_key in self.cache:
                return (self.cache[cache_key],)

            response = model_instance.chat_completion(
                model=model,
                messages=history_messages + [{"role": "user", "content": prompt}],
                max_tokens=int(max_tokens))
            
            self.cache[cache_key] = response
            return (response,)
        except Exception as e:
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            return (str(e), )


class VolcengineTxt2ImgNode:
    platform = "volcengine"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "doubao-seedream-4-0-250828"}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "ratio_or_size": (seedream_image_ratio, {"default": "1:1 2048x2048"}),
                "override_with": ("INT", {"default": 0}),
                "override_height":("INT", {"default": 0}),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15, "step": 1}),
            },
            "optional": {
                # "images": ("IMAGE", {"default": None}),
                "api_key": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2147483647}),
                "watermark": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT", "INT",)
    RETURN_NAMES = ("Image","Width", "Height")
    FUNCTION = "generate"
    CATEGORY = "NYJY/Volcengine"

    def generate(self, model, prompt, ratio_or_size, override_with, override_height, max_images, api_key, seed, watermark):
        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})
            
            if override_with > 0 and override_height >=0:
                ratio_or_size = f"{override_with}x{override_height}"
            elif "x" in ratio_or_size:
                ratio_or_size = ratio_or_size.split(" ")[1]

            input = {
                "prompt": prompt,
                "size": ratio_or_size, 
                "max_images": max_images,
                "seed": seed,
                "watermark": watermark,
            } 

            image_datas = model_instance.i2i(model, input)
            # base64转成comfyui的image类型 
            images = []
            for image_data in image_datas:
                print(image_data.size)
                (width, height) = image_data.size.split("x")
                image = Image.open(io.BytesIO(base64.b64decode(image_data.b64_json)))
                image = np.array(image).astype(np.float32) / 255.0
                images.append(torch.from_numpy(image))  # 转换为torch tensor
           
            return (torch.stack(images, dim=0), width, height)
        except Exception as e:
            # 打印堆栈信息
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            # 返回一个空的图像tensor作为错误处理
            return (torch.zeros((1, 512, 512, 3)),)


class VolcengineImg2ImgNode:
    platform = "volcengine"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "doubao-seedream-4-0-250828"}),
                "images": ("IMAGE", {"default": None}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "ratio_or_size": (seedream_image_ratio, {"default": "1:1 2048x2048"}),
                "override_with": ("INT", {"default": 0}),
                "override_height":("INT", {"default": 0}),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15, "step": 1}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2147483647}),
                "watermark": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT", "INT",)
    RETURN_NAMES = ("Image","Width", "Height")
    FUNCTION = "generate"
    CATEGORY = "NYJY/Volcengine"

    def generate(self, model, images, prompt, ratio_or_size, override_with, override_height, max_images, api_key, seed, watermark):
        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})

            # 将comfyui的image类型转成base64，格式 ：data:image/<图片格式>;base64,<Base64编码>
            images_base64 = []
            for image in images:
                image = image.numpy()
                image = (image * 255).astype(np.uint8)
                image = Image.fromarray(image)
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
                images_base64.append(f"data:image/jpeg;base64,{base64_string}")
            
            if override_with > 0 and override_height >=0:
                ratio_or_size = f"{override_with}x{override_height}"
            elif "x" in ratio_or_size:
                ratio_or_size = ratio_or_size.split(" ")[1]

            input = {
                "prompt": prompt,
                "image": images_base64,
                "size": ratio_or_size, 
                "max_images": max_images,
                "seed": seed,
                "watermark": watermark,
            } 

            image_datas = model_instance.i2i(model, input)
            # base64转成comfyui的image类型 
            images = []
            for image_data in image_datas:
                print(image_data.size)
                (width, height) = image_data.size.split("x")
                image = Image.open(io.BytesIO(base64.b64decode(image_data.b64_json)))
                image = np.array(image).astype(np.float32) / 255.0
                images.append(torch.from_numpy(image))  # 转换为torch tensor
           

            return (torch.stack(images, dim=0), width, height)
        except Exception as e:
            # 打印堆栈信息
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            # 返回一个空的图像tensor作为错误处理
            return (torch.zeros((1, 512, 512, 3)),)