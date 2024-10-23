import math
from nodes import EmptyLatentImage
import torch
import comfy.model_management

radio_list = [
    "自定义",
    "SDXL - 1:1 square 1024x1024",
    "SDXL - 3:4 portrait 896x1152",
    "SDXL - 2:3 portrait 832x1216",
    "SDXL - 9:16 portrait 768x1344",
    "SDXL - 9:19 portrait 704x1472",
    "SD1.5 - 1:1 square 512x521",
    "SD1.5 - 2:3 portrait 512x768",
    "SD1.5 - 3:4 portrait 512x682",
    "SD1.5 - 16:9 cinema 910x512",
    "SD1.5 - 1.85:1 cinema 952x512",
    "SD1.5 - 2:1 cinema 1024x512",
]


class CustomLatentImageNode:
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
                "width": (
                    "INT",
                    {"default": 1216},
                ),
                "height": (
                    "INT",
                    {"default": 832},
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
            [batch_size, 4, upscale_height // 8, upscale_width // 8],
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
