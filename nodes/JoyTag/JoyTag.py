from .models import VisionModel
from PIL import Image
import torch.amp.autocast_mode
from pathlib import Path
import torch
import torchvision.transforms.functional as TVF
from huggingface_hub import snapshot_download
from ..config import LoadConfig
import os
import numpy as np


class JoyTagNode:
    def __init__(self):
        config_data = LoadConfig()
        self.config_data = config_data
        self.model_path = os.path.join(self.config_data["base_path"], "models/joytag/")
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE", {"default": "", "multiline": False}),
                "THRESHOLD": (
                    "FLOAT",
                    {"default": 0.4, "min": 0.1, "max": 1, "step": 0.1},
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "run"

    CATEGORY = "NYJY/image"

    def prepare_image(self, image: Image.Image, target_size: int) -> torch.Tensor:
        # Pad image to square
        image_shape = image.size
        max_dim = max(image_shape)
        pad_left = (max_dim - image_shape[0]) // 2
        pad_top = (max_dim - image_shape[1]) // 2

        padded_image = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
        padded_image.paste(image, (pad_left, pad_top))

        # Resize image
        if max_dim != target_size:
            padded_image = padded_image.resize(
                (target_size, target_size), Image.BICUBIC
            )

        # Convert to tensor
        image_tensor = TVF.pil_to_tensor(padded_image) / 255.0

        # Normalize
        image_tensor = TVF.normalize(
            image_tensor,
            mean=[0.48145466, 0.4578275, 0.40821073],
            std=[0.26862954, 0.26130258, 0.27577711],
        )

        return image_tensor

    def predict(self, image: Image.Image, threshold):
        model = VisionModel.load_model(self.model_path)
        model.eval()
        model = model.to("cuda")

        with open(os.path.join(self.model_path, "top_tags.txt"), "r") as f:
            top_tags = [line.strip() for line in f.readlines() if line.strip()]

        image_tensor = self.prepare_image(image, model.image_size)
        batch = {
            "image": image_tensor.unsqueeze(0).to("cuda"),
        }

        with torch.amp.autocast_mode.autocast("cuda", enabled=True):
            preds = model(batch)
            tag_preds = preds["tags"].sigmoid().cpu()

        scores = {top_tags[i]: tag_preds[0][i] for i in range(len(top_tags))}
        predicted_tags = [tag for tag, score in scores.items() if score > threshold]
        tag_string = ", ".join(predicted_tags)
        return tag_string, scores

    def run(self, image, THRESHOLD):
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        snapshot_download(
            repo_id=self.config_data["joytag"]["hf_project"],
            ignore_patterns=["*.onnx"],
            local_dir=self.model_path,
        )

        i = 255.0 * image[0].cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        tag_string, scores = self.predict(img, THRESHOLD)

        return (tag_string,)
