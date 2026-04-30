from PIL import Image
import numpy as np
import base64
import io as sys_io
import torch
import traceback
import requests

STEPFUN_API_BASE = "https://api.stepfun.com/v1"
MODEL = "step-image-edit-2"

# step-image-edit-2 支持的图像尺寸
STEPFUN_IMAGE_SIZES = [
    "1024x1024",
    "768x1360",
    "896x1184",
    "1360x768",
    "1184x896",
]


def _get_api_key(api_key_input):
    if api_key_input and api_key_input.strip():
        return api_key_input.strip()
    try:
        from ..config import LoadConfig
        config = LoadConfig()
        return config.get("stepfun", {}).get("api_key", "")
    except Exception as e:
        print(f"[StepFun] 读取配置文件失败: {e}")
        return ""


def _tensor_to_png_bytes(image_tensor):
    """ComfyUI 单张图像 tensor → PNG 字节"""
    i = 255.0 * image_tensor.cpu().numpy()
    pil = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
    if pil.mode != "RGB":
        pil = pil.convert("RGB")
    buf = sys_io.BytesIO()
    pil.save(buf, format="PNG")
    return buf.getvalue()


def _b64_to_tensor(b64_string):
    """base64 图像字符串 → ComfyUI 图像 tensor (1, H, W, 3)"""
    image_data = base64.b64decode(b64_string)
    pil = Image.open(sys_io.BytesIO(image_data)).convert("RGB")
    arr = np.array(pil).astype(np.float32) / 255.0
    return torch.from_numpy(arr).unsqueeze(0)


class StepFunTxt2ImgNode:
    """StepFun 文生图节点，使用 step-image-edit-2 模型"""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "size": (STEPFUN_IMAGE_SIZES, {"default": "1024x1024"}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "steps": ("INT", {"default": 8, "min": 1, "max": 50, "step": 1}),
                "cfg_scale": ("FLOAT", {"default": 1.0, "min": 1.0, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "text_mode": ("BOOLEAN", {"default": False}),
                "timeout": ("INT", {"default": 60, "min": 10, "max": 600, "step": 1}),
                "api_key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"
    CATEGORY = "NYJY/StepFun"

    def generate(self, prompt, size, negative_prompt="", steps=8, cfg_scale=1.0,
                 seed=0, text_mode=False, timeout=60, api_key=""):
        try:
            api_key = _get_api_key(api_key)
            if not api_key:
                raise ValueError("未设置 StepFun API Key，请在节点中输入或在 config.json 中配置 stepfun.api_key")

            timeout = max(1, int(timeout))
            if not prompt or not prompt.strip():
                raise ValueError("prompt 不能为空")
            if len(prompt) > 512:
                print("[StepFun] 警告：prompt 超过 512 字符，将被截断")
                prompt = prompt[:512]
            if negative_prompt and len(negative_prompt) > 512:
                print("[StepFun] 警告：negative_prompt 超过 512 字符，将被截断")
                negative_prompt = negative_prompt[:512]

            print(f"[StepFun] 文生图开始 | 模型: {MODEL} | 尺寸: {size} | steps: {steps} | cfg_scale: {cfg_scale} | timeout: {timeout}s")
            print(f"[StepFun] prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

            # 调换宽高：将 size 字符串中的 "宽x高" 转为 "高x宽"
            if 'x' in size:
                w, h = size.split('x')
                size = f"{h}x{w}"
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "size": size,
                "n": 1,
                "response_format": "b64_json",
                "steps": steps,
                "cfg_scale": cfg_scale,
                "text_mode": text_mode,
            }
            if negative_prompt:
                payload["negative_prompt"] = negative_prompt
            # seed=0 视为不传（由服务端随机生成）
            if seed > 0:
                payload["seed"] = seed

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            print(f"[StepFun] 发送请求 → POST {STEPFUN_API_BASE}/images/generations")
            response = requests.post(
                f"{STEPFUN_API_BASE}/images/generations",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            if response.status_code != 200:
                try:
                    err = response.json()
                except Exception:
                    err = response.text
                raise Exception(f"API 请求失败 HTTP {response.status_code}: {err}")

            result = response.json()
            print(f"[StepFun] 请求成功 | request_id: {result.get('id', 'N/A')}")

            data = result.get("data", [])
            if not data:
                raise Exception("API 返回数据为空")

            item = data[0]
            finish_reason = item.get("finish_reason", "")
            actual_seed = item.get("seed", seed)
            print(f"[StepFun] 文生图完成 | finish_reason: {finish_reason} | seed: {actual_seed}")

            if finish_reason == "content_filtered":
                raise Exception("图片内容被安全策略过滤，请修改 prompt 后重试")

            b64 = item.get("b64_json", "")
            if not b64:
                raise Exception("API 返回数据中缺少 b64_json 字段")

            tensor = _b64_to_tensor(b64)
            print(f"[StepFun] 图片解码成功 | shape: {tensor.shape}")
            return (tensor,)

        except Exception as e:
            traceback.print_exc()
            print(f"[StepFun] 文生图失败: {e}")
            return (torch.zeros((1, 512, 512, 3)),)


class StepFunImgEditNode:
    """StepFun 图片编辑节点，使用 step-image-edit-2 模型"""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "steps": ("INT", {"default": 8, "min": 1, "max": 50, "step": 1}),
                "cfg_scale": ("FLOAT", {"default": 1.0, "min": 1.0, "max": 10.0, "step": 0.1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "text_mode": ("BOOLEAN", {"default": False}),
                "timeout": ("INT", {"default": 60, "min": 10, "max": 600, "step": 1}),
                "api_key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "edit"
    CATEGORY = "NYJY/StepFun"

    def edit(self, image, prompt, negative_prompt="", steps=8, cfg_scale=1.0,
             seed=0, text_mode=False, timeout=60, api_key=""):
        try:
            api_key = _get_api_key(api_key)
            if not api_key:
                raise ValueError("未设置 StepFun API Key，请在节点中输入或在 config.json 中配置 stepfun.api_key")

            timeout = max(1, int(timeout))
            if not prompt or not prompt.strip():
                raise ValueError("prompt 不能为空")
            if len(prompt) > 512:
                print("[StepFun] 警告：prompt 超过 512 字符，将被截断")
                prompt = prompt[:512]
            if negative_prompt and len(negative_prompt) > 512:
                print("[StepFun] 警告：negative_prompt 超过 512 字符，将被截断")
                negative_prompt = negative_prompt[:512]

            # step-image-edit-2 最大支持 4096x4096
            h, w = image.shape[1], image.shape[2]
            if w > 4096 or h > 4096:
                raise ValueError(f"图片尺寸 {w}x{h} 超过最大限制 4096x4096，请缩小后再试")

            print(f"[StepFun] 图片编辑开始 | 模型: {MODEL} | 输入尺寸: {w}x{h} | steps: {steps} | cfg_scale: {cfg_scale} | timeout: {timeout}s")
            print(f"[StepFun] prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

            image_bytes = _tensor_to_png_bytes(image[0])
            print(f"[StepFun] 图片已转换为 PNG | 大小: {len(image_bytes):,} 字节")

            headers = {
                "Authorization": f"Bearer {api_key}",
            }
            files = {
                "image": ("image.png", image_bytes, "image/png"),
            }
            form_data = {
                "model": MODEL,
                "prompt": prompt,
                "steps": str(steps),
                "cfg_scale": str(cfg_scale),
                "response_format": "b64_json",
                "text_mode": "true" if text_mode else "false",
            }
            if negative_prompt:
                form_data["negative_prompt"] = negative_prompt
            if seed > 0:
                form_data["seed"] = str(seed)

            print(f"[StepFun] 发送请求 → POST {STEPFUN_API_BASE}/images/edits")
            response = requests.post(
                f"{STEPFUN_API_BASE}/images/edits",
                headers=headers,
                files=files,
                data=form_data,
                timeout=timeout,
            )

            if response.status_code != 200:
                try:
                    err = response.json()
                except Exception:
                    err = response.text
                raise Exception(f"API 请求失败 HTTP {response.status_code}: {err}")

            result = response.json()
            print(f"[StepFun] 请求成功 | request_id: {result.get('id', 'N/A')}")

            data = result.get("data", [])
            if not data:
                raise Exception("API 返回数据为空")

            item = data[0]
            finish_reason = item.get("finish_reason", "")
            actual_seed = item.get("seed", seed)
            print(f"[StepFun] 图片编辑完成 | finish_reason: {finish_reason} | seed: {actual_seed}")

            if finish_reason == "content_filtered":
                raise Exception("图片内容被安全策略过滤，请修改 prompt 后重试")

            b64 = item.get("b64_json", "")
            if not b64:
                raise Exception("API 返回数据中缺少 b64_json 字段")

            tensor = _b64_to_tensor(b64)
            print(f"[StepFun] 图片解码成功 | shape: {tensor.shape}")
            return (tensor,)

        except Exception as e:
            traceback.print_exc()
            print(f"[StepFun] 图片编辑失败: {e}")
            return (torch.zeros((1, 512, 512, 3)),)
