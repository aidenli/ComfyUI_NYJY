import math
import torch
import comfy.model_management
import re
from nodes import MAX_RESOLUTION

sdxl_ratio_list = [
    "1:2 - 704x1408",
    "11:21 - 704x1344",
    "9:19 - 704x1472",
    "4:7 - 768x1344",
    "3:5 - 768x1280",
    "5:8 - 768x1216",
    "13:19 - 832x1216",
    "13:18 - 832x1152",
    "7:9 - 896x1152",
    "14:17 - 896x1088",
    "15:17 - 960x1088",
    "15:16 - 960x1024",
    "1:1 - 1024x1024",
    "16:15 - 1024x960",
    "17:15 - 1088x960",
    "17:14 - 1088x896",
    "9:7 - 1152x896",
    "18:13 - 1152x832",
    "19:13 - 1216x832",
    "8:5 - 1216x768",
    "5:3 - 1280x768",
    "7:4 - 1344x768",
    "21:11 - 1344x704",
    "2:1 - 1408x704",
    "23:11 - 1472x704",
    "12:5 - 1536x640",
    "5:2 - 1600x640",
    "26:9 - 1664x576",
    "3:1 - 1728x576",
]

sdxl_ratio_list_map = {}
for s in sdxl_ratio_list:
    m = re.findall(r"(\d+)x(\d+)$", s)
    if m:
        sdxl_ratio_list_map[s] = (int(m[0][0]), int(m[0][1]))


qwen_image_list = [
    "1:1 - 1328x1328",
    "3:4 - 1104x1472",
    "2:3 - 1056x1584",
    "9:16 - 936x1664",
    "9:21 - 864x2016",
    "4:3 - 1472x1104",
    "3:2 - 1584x1056",
    "16:9 - 1664x936",
    "21:9 - 2016x864",
]

qwen_image_list_map = {
    "1:1 - 1328x1328": (1328, 1328),
    "3:4 - 1104x1472": (1104, 1472),
    "2:3 - 1056x1584": (1056, 1584),
    "9:16 - 936x1664": (936, 1664),
    "9:21 - 864x2016": (864, 2016),
    "4:3 - 1472x1104": (1472, 1104),
    "3:2 - 1584x1056": (1584, 1056),
    "16:9 - 1664x936": (1664, 936),
    "21:9 - 2016x864": (2016, 864),
}

class CustomLatentImageNode:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ratio": (
                    sdxl_ratio_list,
                    {"default": "13:19 - 832x1216"},
                ),
                "switch_width_height": (
                    "BOOLEAN",
                    {"default": False},
                ),
                "width_override": (
                    "INT",
                    {"default": 0, "step": 8, "min": 0, "max": MAX_RESOLUTION},
                ),
                "height_override": (
                    "INT",
                    {"default": 0, "step": 8, "min": 0, "max": MAX_RESOLUTION},
                ),
                "upscale_factor": (
                    "FLOAT",
                    {
                        "default": 1,
                        "step": 0.1,
                        "min": 0.125,
                        "max": 100000
                    },
                ),
                "batch_size": (
                    "INT",
                    {"default": 1, "min": 1, "max": 100},
                ),
            }
        }

    RETURN_TYPES = (
        "LATENT",
        "INT",
        "INT",
        "FLOAT",
        "INT",
        "INT",
    )
    RETURN_NAMES = (
        "LATENT",
        "width",
        "height",
        "upscale_factor",
        "upscale_width",
        "upscale_height",
    )
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "NYJY"

    def run(
        self, ratio, switch_width_height, width_override, height_override, upscale_factor, batch_size
    ):
        width, height = sdxl_ratio_list_map[ratio]
        if width_override > 0:
            width = width_override
        if height_override > 0:
            height = height_override

        safe_factor = upscale_factor if upscale_factor > 0 else 1
        upscale_width = min(MAX_RESOLUTION, round_to_eight(width * safe_factor))
        upscale_height = min(MAX_RESOLUTION, round_to_eight(height * safe_factor))

        if switch_width_height:
            (width, height) = (height, width)
            (upscale_width, upscale_height) = (upscale_height, upscale_width)
            
        latent = torch.zeros(
            [batch_size, 4, height // 8, width // 8],
            device=comfy.model_management.intermediate_device(),
        )
        return {
            "result": (
                {"samples": latent},
                width,
                height,
                upscale_factor,
                upscale_width,
                upscale_height,
            )
        }


class CustomLatentImageSimpleNode:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ratio": (
                    sdxl_ratio_list,
                    {"default": "13:19 - 832x1216"},
                ),
                "switch_width_height": (
                    "BOOLEAN",
                    {"default": False},
                ),
                "batch_size": (
                    "INT",
                    {"default": 1, "min": 1, "max": 100},
                ),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("LATENT",)
    FUNCTION = "run"
    CATEGORY = "NYJY"

    def run(self, ratio, switch_width_height, batch_size):
        width, height = sdxl_ratio_list_map[ratio]
        if switch_width_height:
            (width, height) = (height, width)

        latent = torch.zeros(
            [batch_size, 4, height // 8, width // 8],
            device=comfy.model_management.intermediate_device(),
        )
        return {"result": ({"samples": latent},)}

def round_to_eight(num):
    return max(8, int(math.ceil(num / 8) * 8))

class QwenLatentImageNode:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "ratio": (
                    qwen_image_list,
                    {"default": "1:1 - 1328x1328"},
                ),
                "batch_size": (
                    "INT",
                    {"default": 1, "min": 1, "max": 100},
                ),
                "width_override": (
                    "INT",
                    {"default": 0, "step": 8, "min": 0, "max": MAX_RESOLUTION},
                ),
                "height_override": (
                    "INT",
                    {"default": 0, "step": 8, "min": 0, "max": MAX_RESOLUTION},
                ),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("LATENT", "width", "height")
    FUNCTION = "run"
    CATEGORY = "NYJY"

    def run(self, ratio, batch_size, width_override, height_override):
        width, height = qwen_image_list_map[ratio]
        if width_override > 0:
            width = width_override
        if height_override > 0:
            height = height_override
            
        latent = torch.zeros(
            [batch_size, 4, height // 8, width // 8],
            device=comfy.model_management.intermediate_device(),
        )
        return {"result": ({"samples": latent}, width, height)}
