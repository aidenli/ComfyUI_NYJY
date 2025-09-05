import math
from nodes import EmptyLatentImage
import torch
import comfy.model_management
import re

radio_list = [
    "SDXL - 1:1 square 1024x1024",
    "SDXL - 2:3 portrait 832x1216",
    "SDXL - 3:4 portrait 896x1152",
    "SDXL - 5:8 portrait 768x1216",
    "SDXL - 9:16 portrait 768x1344",
    "SDXL - 9:19 portrait 704x1472",
    "SDXL - 9:21 portrait 640x1536",
    "SD1.5 - 1:1 square 512x512",
    "SD1.5 - 2:3 portrait 512x768",
    "SD1.5 - 3:4 portrait 512x682",
    "SD1.5 - 16:9 cinema 910x512",
    "SD1.5 - 1.85:1 cinema 952x512",
    "SD1.5 - 2:1 cinema 1024x512",
]

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
                "radio": (
                    ["自定义"] + radio_list,
                    {"default": "SDXL - 2:3 portrait 832x1216"},
                ),
                "switch_width_height": (
                    "BOOLEAN",
                    {"default": False},
                ),
                "width": (
                    "INT",
                    {"default": 832},
                ),
                "height": (
                    "INT",
                    {"default": 1216},
                ),
                "upscale_factor": (
                    "FLOAT",
                    {
                        "default": 1,
                        "step": 0.1,
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
        self, radio, switch_width_height, width, height, upscale_factor, batch_size
    ):
        upscale_width = math.ceil(width * upscale_factor)
        upscale_height = math.ceil(height * upscale_factor)
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
                "radio": (
                    radio_list,
                    {"default": "SDXL - 2:3 portrait 832x1216"},
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

    def run(self, radio, switch_width_height, batch_size):
        extracted = re.findall(r"(\d+)x(\d+)$", radio)
        width = int(extracted[0][0])
        height = int(extracted[0][1])
        if switch_width_height:
            (width, height) = (height, width)

        latent = torch.zeros(
            [batch_size, 4, height // 8, width // 8],
            device=comfy.model_management.intermediate_device(),
        )
        return {"result": ({"samples": latent},)}

class QwenLatentImageNode:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "radio": (
                    qwen_image_list,
                    {"default": "1:1 - 1328x1328"},
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

    def run(self, radio, batch_size):
        width, height = qwen_image_list_map[radio]
        latent = torch.zeros(
            [batch_size, 4, height // 8, width // 8],
            device=comfy.model_management.intermediate_device(),
        )
        return {"result": ({"samples": latent},)}