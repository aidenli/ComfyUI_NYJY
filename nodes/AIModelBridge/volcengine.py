from .api import AIModelBridgeFactory, ModelOptionBase
from .definition import *
from PIL import Image
import numpy as np
import base64
import io
import json
import torch
import hashlib
import traceback


def extract_image_size(image_datas, default_width=512, default_height=512):
    """
    从图像数据中提取尺寸信息
    
    Args:
        image_datas: 图像数据列表
        default_width: 默认宽度
        default_height: 默认高度
        
    Returns:
        tuple: (width, height) 图像尺寸
    """
    width, height = default_width, default_height
    if image_datas and hasattr(image_datas[0], 'size'):
        width, height = image_datas[0].size.split("x")
        width, height = int(width), int(height)
    return width, height


class ImageConverter:
    """图像格式转换工具类"""
    
    @staticmethod
    def base64_to_comfyui_image(base64_string):
        """
        将base64图像数据转换为ComfyUI的image格式
        
        Args:
            base64_string: base64编码的图像字符串
            
        Returns:
            torch.Tensor: ComfyUI格式的图像tensor
        """
        image = Image.open(io.BytesIO(base64.b64decode(base64_string)))
        image = np.array(image).astype(np.float32) / 255.0
        tensor_image = torch.from_numpy(image)
        return tensor_image
    
    @staticmethod
    def comfyui_image_to_base64(image, format="JPEG"):
        """
        将ComfyUI的image格式转换为base64字符串
        
        Args:
            image: ComfyUI的torch.Tensor图像
            format: 图像格式，默认为JPEG
            
        Returns:
            str: base64编码的图像字符串，格式为 data:image/<format>;base64,<base64_string>
        """
        image = image.numpy()
        image = (image * 255).astype(np.uint8)
        pil_image = Image.fromarray(image)
        buffered = io.BytesIO()
        pil_image.save(buffered, format=format)
        base64_string = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/{format.lower()};base64,{base64_string}"
    
    @staticmethod
    def batch_base64_to_comfyui_images(base64_strings):
        """
        批量将base64图像数据转换为ComfyUI的image格式
        
        Args:
            base64_strings: base64编码的图像字符串列表
            
        Returns:
            torch.Tensor: 堆叠的图像tensor
        """
        images = []
        
        for base64_string in base64_strings:
            tensor_image = ImageConverter.base64_to_comfyui_image(base64_string)
            images.append(tensor_image)
        
        return torch.stack(images, dim=0)
    
    @staticmethod
    def batch_comfyui_images_to_base64(images, format="JPEG"):
        """
        批量将ComfyUI的image格式转换为base64字符串列表
        
        Args:
            images: ComfyUI的torch.Tensor图像批次
            format: 图像格式，默认为JPEG
            
        Returns:
            list: base64编码的图像字符串列表
        """
        images_base64 = []
        for image in images:
            base64_string = ImageConverter.comfyui_image_to_base64(image, format)
            images_base64.append(base64_string)
        return images_base64

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

            response = model_instance.chat_completion(
                model=model,
                messages=history_messages + [{"role": "user", "content": prompt}],
                max_tokens=int(max_tokens))
        
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
                "ratio_or_size": (seedream4_image_ratio, {"default": "1:1 2048x2048"}),
                "override_with": ("INT", {"default": 0}),
                "override_height":("INT", {"default": 0}),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15, "step": 1}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "watermark": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT", "INT",)
    RETURN_NAMES = ("Image","Width", "Height")
    FUNCTION = "generate"
    CATEGORY = "NYJY/Volcengine"

    def generate(self, model, prompt, ratio_or_size, override_with, override_height, max_images, api_key, watermark):
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
                "watermark": watermark,
            } 

            image_datas = model_instance.i2i(model, input)
            
            # 提取base64字符串列表
            base64_strings = [image_data.b64_json  for image_data in image_datas]
            
            # 获取第一张图片的尺寸信息
            width, height = extract_image_size(image_datas)
            
            # 转换图片
            images_tensor = ImageConverter.batch_base64_to_comfyui_images(base64_strings)
            return (images_tensor, width, height)
        except Exception as e:
            # 打印堆栈信息
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            # 返回一个空的图像tensor作为错误处理
            return (torch.zeros((1, 512, 512, 3)),)

class Seedream4Txt2ImgNode(VolcengineTxt2ImgNode):
    pass

class VolcengineImg2ImgNode:
    platform = "volcengine"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "doubao-seedream-4-0-250828"}),
                "images": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "ratio_or_size": (seedream4_image_ratio, {"default": "1:1 2048x2048"}),
                "override_with": ("INT", {"default": 0}),
                "override_height":("INT", {"default": 0}),
                "max_images": ("INT", {"default": 1, "min": 1, "max": 15, "step": 1}),
            },
            "optional": {
                "api_key": ("STRING", {"default": ""}),
                "watermark": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT", "INT",)
    RETURN_NAMES = ("Image","Width", "Height")
    FUNCTION = "generate"
    CATEGORY = "NYJY/Volcengine"

    def generate(self, model, images, prompt, ratio_or_size, override_with, override_height, max_images, api_key, watermark):
        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})

            # 使用ImageConverter批量转换comfyui的image类型到base64
            images_base64 = ImageConverter.batch_comfyui_images_to_base64(images)
            
            if override_with > 0 and override_height >=0:
                ratio_or_size = f"{override_with}x{override_height}"
            elif "x" in ratio_or_size:
                ratio_or_size = ratio_or_size.split(" ")[1]

            input = {
                "prompt": prompt,
                "image": images_base64,
                "size": ratio_or_size, 
                "max_images": max_images,
                "watermark": watermark,
            } 

            image_datas = model_instance.i2i(model, input)
            
            # 提取base64字符串列表
            base64_strings = [image_data.b64_json  for image_data in image_datas]
            
            # 获取第一张图片的尺寸信息
            width, height = extract_image_size(image_datas)
            
            # 转换图片
            images_tensor = ImageConverter.batch_base64_to_comfyui_images(base64_strings)
            return (images_tensor, width, height)
        except Exception as e:
            # 打印堆栈信息
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            # 返回一个空的图像tensor作为错误处理
            return (torch.zeros((1, 512, 512, 3)),)

class Seedream4Img2ImgNode(VolcengineImg2ImgNode):
    pass


class Seedream3Txt2ImgNode:
    platform = "volcengine"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "doubao-seedream-3-0-t2i-250415"}),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "ratio": (seedream3_image_ratio, {"default": "1:1 1024x1024"}),
                "override_with": ("INT", {"default": 0}),
                "override_height":("INT", {"default": 0}),
            },
            "optional": {
                "guidance_scale": ("FLOAT", {"default": 2.5, "min":1, "max": 10, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "api_key": ("STRING", {"default": ""}),
                "watermark": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT", "INT",)
    RETURN_NAMES = ("Image","Width", "Height")
    FUNCTION = "generate"
    CATEGORY = "NYJY/Volcengine"

    def generate(self, model, prompt, ratio, override_with, override_height, guidance_scale, seed, api_key, watermark):
        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})
            
            if override_with > 0 and override_height >=0:
                size = f"{override_with}x{override_height}"
            elif "x" in ratio:
                size = ratio.split(" ")[1]
            else:
                size = ratio

            input = {
                "prompt": prompt,
                "size": size, 
                "guidance_scale": guidance_scale,
                "seed": seed,
                "watermark": watermark,
            } 

            image_datas = model_instance.i2i(model, input)
            
            # 提取base64字符串列表
            base64_strings = [image_data.b64_json  for image_data in image_datas]
            
            # 获取第一张图片的尺寸信息
            width, height = extract_image_size(image_datas)
            
            # 转换图片
            images_tensor = ImageConverter.batch_base64_to_comfyui_images(base64_strings)
            return (images_tensor, width, height)
        except Exception as e:
            # 打印堆栈信息
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            # 返回一个空的图像tensor作为错误处理
            return (torch.zeros((1, 512, 512, 3)),)

class Seededit3Node:
    platform = "volcengine"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": ("STRING", {"default": "doubao-seededit-3-0-i2i-250628"}),
                "images": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "guidance_scale": ("FLOAT", {"default": 5.5, "min":1, "max": 10, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "api_key": ("STRING", {"default": ""}),
                "watermark": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE","INT", "INT",)
    RETURN_NAMES = ("Image","Width", "Height")
    FUNCTION = "generate"
    CATEGORY = "NYJY/Volcengine"

    def generate(self, model, images, prompt, guidance_scale, seed, api_key, watermark):
        try:
            factory = AIModelBridgeFactory()
            model_instance = factory.get_model(self.platform)
            if api_key != "":
                model_instance.set_config({"api_key": api_key})

            # 使用ImageConverter转换comfyui的image类型到base64（只支持单张图片）
            images_base64 = []
            for image in images:
                base64_string = ImageConverter.comfyui_image_to_base64(image)
                images_base64.append(base64_string)
                break   # 只支持单张图片
            
            input = {
                "prompt": prompt,
                "image": images_base64,
                "guidance_scale": guidance_scale,
                "seed": seed,
                "watermark": watermark,
            } 

            image_datas = model_instance.i2i(model, input)
            
            # 提取base64字符串列表
            base64_strings = [image_data.b64_json  for image_data in image_datas]
            
            # 获取第一张图片的尺寸信息
            width, height = extract_image_size(image_datas)
            
            # 转换图片
            images_tensor = ImageConverter.batch_base64_to_comfyui_images(base64_strings)
            return (images_tensor, width, height)
        except Exception as e:
            # 打印堆栈信息
            traceback.print_exc()
            print(f"调用模型[{self.platform} -- {model}]失败：", str(e))
            # 返回一个空的图像tensor作为错误处理
            return (torch.zeros((1, 512, 512, 3)),)