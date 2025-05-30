import folder_paths
from gradio_client import Client
import os
import node_helpers
import torch
import numpy as np
from PIL import Image, ImageOps, ImageSequence
from .utils import print_log

SERVER_NAMES = {
    "google_us": "Google US Server",
    "azure_lite": "Azure Lite Supercomputer Server",
    "artemis": "Artemis GPU Super cluster",
    "nb_dr": "NebulaDrive Tensor Server",
    "pixelnet": "PixelNet NPU Server",
    "nsfw_core": "NSFW-Core: Uncensored Server",
    "nsfw_core_2": "NSFW-Core: Uncensored Server 2",
    "nsfw_core_3": "NSFW-Core: Uncensored Server 3",
    "nsfw_core_4": "NSFW-Core: Uncensored Server 4",
}

API_NAME = "/generate_image"

class FluxProOnlineNode:
    def __init__(self) -> None:
        self.output_dir = folder_paths.get_temp_directory()
        self.filename_prefix = "flux_pro"

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "width": ("INT", {"default": 1280, "min": 512, "max": 2048}),
                "height": ("INT", {"default": 1280, "min": 512, "max": 2048}),
                "seed": ("INT", {"default": 1234, "min": 0, "max": 2147483647}),
                "server_choice": (list(SERVER_NAMES.keys()),{"default": "google_us"},
                ),
            }
        }
        
    RETURN_TYPES = ("IMAGE",)
    OUTPUT_IS_LIST = (False,)
    RETURN_NAMES = ("image",)
    FUNCTION = "run"
    CATEGORY = "NYJY"

    def get_output_image(self, image_path):
        try:
            img = node_helpers.pillow(Image.open, image_path)

            output_images = []
            excluded_formats = ["MPO"]
            for i in ImageSequence.Iterator(img):
                i = node_helpers.pillow(ImageOps.exif_transpose, i)

                if i.mode == "I":
                    i = i.point(lambda i: i * (1 / 255))
                image = i.convert("RGB")

                image = np.array(image).astype(np.float32) / 255.0
                image = torch.from_numpy(image)[None,]
                output_images.append(image)

            if len(output_images) > 1 and img.format not in excluded_formats:
                output_image = torch.cat(output_images, dim=0)
            else:
                output_image = output_images[0]

            return output_image
        except Exception as e:
            print_log(f"获取图片失败[{image_id}]:{e}")
            return None

    def run(
        self, prompt, width, height, seed, server_choice
    ):
        client = Client("NihalGazi/FLUX-Pro-Unlimited", download_files=self.output_dir)
        result = client.predict(
            prompt=prompt,
            width=width,
            height=height,
            seed=seed,
            randomize=False,
            server_choice=SERVER_NAMES.get(server_choice),
            api_name=API_NAME,
        )

        file_path = result[0]
        previews = [{
            "filename": file_path.split("\\")[-1],
            "subfolder": file_path.split("\\")[-2],
            "type": "temp",
        }]
        return {
            "ui": {"images": previews,},
            "result": (self.get_output_image(result[0]),)
        }