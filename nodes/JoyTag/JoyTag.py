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
import json
import re
import folder_paths
import shutil
from ..utils import print_log


class JoyTagNode:
    def __init__(self):
        config_data = LoadConfig()
        self.config_data = config_data
        self.model_path = os.path.join(self.config_data["base_path"], "models/joytag/")
        self.clip_model_path = os.path.join(
            folder_paths.get_folder_paths("clip")[0], "joytag"
        )
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
                "positive": (
                    "STRING",
                    {
                        "multiline": True,
                        "placeholder": "添加需要增加的正向提示词到此处，多个以逗号分隔",
                    },
                ),
                "nagetive": (
                    "STRING",
                    {
                        "multiline": True,
                        "placeholder": "添加需要增加的负面提示词到此处，多个以逗号分隔",
                    },
                ),
                "safe_mode": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    FUNCTION = "run"
    OUTPUT_NODE = False
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
        model = VisionModel.load_model(self.clip_model_path)
        model.eval()
        model = model.to("cuda")

        with open(os.path.join(self.clip_model_path, "top_tags.txt"), "r") as f:
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

    def run(self, image, THRESHOLD, positive, nagetive, safe_mode):
        # 创建模型目录
        if not os.path.exists(self.clip_model_path):
            os.mkdir(self.clip_model_path)

        # 移动旧文件
        if os.path.exists(self.model_path):
            for file in os.listdir(self.model_path):
                source_file = os.path.join(self.model_path, file)
                target_file = os.path.join(self.clip_model_path, file)
                shutil.move(source_file, target_file)
            shutil.rmtree(os.path.join(self.config_data["base_path"], "models"))

        # 如果没有模型文件就下载
        if (
            os.path.exists(os.path.join(self.clip_model_path, "model.safetensors"))
            == False
        ) or (
            os.path.exists(os.path.join(self.clip_model_path, "top_tags.txt")) == False
        ):
            print_log(f"开始下载模型到：{self.clip_model_path}")
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
            snapshot_download(
                repo_id=self.config_data["joytag"]["hf_project"],
                ignore_patterns=["*.onnx"],
                local_dir=self.clip_model_path,
            )

        i = 255.0 * image[0].cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        tag_string, scores = self.predict(img, THRESHOLD)
        # 将结果tag转成数组
        arr_predict_tags = re.split(r"[,，\n]", tag_string)
        arr_predict_tags = [str.strip() for str in arr_predict_tags]
        # 需要过滤负面提示词
        arr_nagetive = re.split(r"[,，\n]", nagetive)
        arr_nagetive = [str.strip() for str in arr_nagetive]

        if safe_mode == True:
            # 读取预设的负面提示词
            with open(
                os.path.join(
                    self.config_data["base_path"], "nodes/JoyTag/filter_tags.json"
                ),
                "r",
            ) as f:
                presets = f.read()
                if len(nagetive.strip()) > 0:
                    arr_nagetive = arr_nagetive + json.loads(presets)
                else:
                    arr_nagetive = json.loads(presets)

        arr_filter = []
        for result_tag in arr_predict_tags:
            is_match = False
            for nagetive_tag in arr_nagetive:
                if nagetive_tag.strip() == "":
                    continue

                if result_tag.strip() == "" or nagetive_tag in result_tag:
                    is_match = True
                    break

            if is_match == False:
                arr_filter.append(result_tag)

        # 连接正面提示词
        if len(positive) > 0:
            return (positive + "\n" + (",".join(arr_filter)),)
        else:
            return (",".join(arr_filter),)
