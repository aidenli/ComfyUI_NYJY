from torch import nn
from transformers import (
    AutoModel,
    AutoProcessor,
    AutoTokenizer,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    AutoModelForCausalLM,
)
from ..config import LoadConfig, print_log
import os
from huggingface_hub import snapshot_download
import torch
from PIL import Image
import numpy as np
from pathlib import Path
from .online import joy_caption_online
from ..utils import create_nonceid
import time

config_data = LoadConfig()

CLIP_MODEL = "google/siglip-so400m-patch14-384"
CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "wpkklhc6/image_adapter.pt")

dict_models = {"Meta-Llama-3.1-8B-bnb-4bit": "unsloth/Meta-Llama-3.1-8B-bnb-4bit"}


class ImageAdapter(nn.Module):
    def __init__(self, input_features: int, output_features: int):
        super().__init__()
        self.linear1 = nn.Linear(input_features, output_features)
        self.activation = nn.GELU()
        self.linear2 = nn.Linear(output_features, output_features)

    def forward(self, vision_outputs: torch.Tensor):
        x = self.linear1(vision_outputs)
        x = self.activation(x)
        x = self.linear2(x)
        return x


class LlamaModel:
    def __init__(self, model_id):
        model_name = dict_models[model_id]
        MODEL_PATH = os.path.join(config_data["base_path"], f"./models/{model_name}")

        if not os.path.exists(MODEL_PATH):
            MODEL_PATH = os.path.join(
                config_data["base_path"], f"../../models/llm/{model_id}"
            )
            if not os.path.exists(MODEL_PATH):
                print_log(f"start download LLM: {model_name}")
                snapshot_download(repo_id=model_name, local_dir=MODEL_PATH)

        # LLM
        print_log(f"Loading LLM: {model_name}")
        text_model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH, device_map="auto", torch_dtype=torch.bfloat16
        )
        text_model.eval()

        # Tokenizer
        print_log(f"Loading tokenizer: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=False)
        assert isinstance(tokenizer, PreTrainedTokenizer) or isinstance(
            tokenizer, PreTrainedTokenizerFast
        ), f"Tokenizer is of type {type(tokenizer)}"
        self.text_model = text_model
        self.tokenizer = tokenizer


class JoyCaptionNode:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": (
                    "STRING",
                    {
                        "default": "A descriptive caption for this image:\n",
                        "multiline": True,
                    },
                ),
                "model": (
                    [
                        "Meta-Llama-3.1-8B-bnb-4bit",
                    ],
                    {"default": "Meta-Llama-3.1-8B-bnb-4bit"},
                ),
                "max_new_tokens": (
                    "INT",
                    {"default": 300, "min": 10, "max": 1000, "step": 1},
                ),
                "top_k": ("INT", {"default": 10, "min": 1, "max": 100, "step": 1}),
                "temperature": (
                    "FLOAT",
                    {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "clear_cache": ("BOOLEAN", {"default": False}),
                "newbie": ("BOOLEAN", {"default": False}),
            }
        }

    CATEGORY = "NYJY/image"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("captions",)
    FUNCTION = "run"

    llama_model = None
    clip_model = None

    def run_local(
        self, model, image, prompt, max_new_tokens, top_k, temperature, clear_cache
    ):
        if self.llama_model is None:
            # load LLM
            self.llama_model = LlamaModel(model)

        if self.clip_model is None:
            # load clip
            CLIP_PATH = os.path.join(
                config_data["base_path"], f"models/clip/{CLIP_MODEL}"
            )
            if not os.path.exists(CLIP_PATH):
                CLIP_PATH = os.path.join(
                    config_data["base_path"],
                    f"../../models/clip/siglip-so400m-patch14-384",
                )

                if not os.path.exists(CLIP_PATH):
                    print_log(f"start download clip: {CLIP_MODEL}")
                    snapshot_download(repo_id=CLIP_MODEL, local_dir=CLIP_PATH)

            # Load CLIP
            print_log(f"Loading CLIP: {CLIP_MODEL}")
            self.clip_processor = AutoProcessor.from_pretrained(CLIP_PATH)
            clip_model = AutoModel.from_pretrained(CLIP_PATH)
            self.clip_model = clip_model.vision_model
            self.clip_model.eval()
            self.clip_model.requires_grad_(False)
            self.clip_model.to("cuda")

        # Image Adapter
        print("Loading image adapter")
        image_adapter = ImageAdapter(
            self.clip_model.config.hidden_size,
            self.llama_model.text_model.config.hidden_size,
        )
        image_adapter.load_state_dict(torch.load(CHECKPOINT_PATH, map_location="cpu"))
        image_adapter.eval()
        image_adapter.to("cuda")

        i = 255.0 * image[0].cpu().numpy()
        input_image = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

        # Preprocess image
        image = self.clip_processor(
            images=input_image, return_tensors="pt"
        ).pixel_values
        image = image.to("cuda")

        # Tokenize the prompt
        prompt = self.llama_model.tokenizer.encode(
            prompt,
            return_tensors="pt",
            padding=False,
            truncation=False,
            add_special_tokens=False,
        )

        # Embed image
        with torch.amp.autocast_mode.autocast("cuda", enabled=True):
            vision_outputs = self.clip_model(
                pixel_values=image, output_hidden_states=True
            )
            image_features = vision_outputs.hidden_states[-2]
            embedded_images = image_adapter(image_features)
            embedded_images = embedded_images.to("cuda")

        # Embed prompt
        prompt_embeds = self.llama_model.text_model.model.embed_tokens(
            prompt.to("cuda")
        )
        assert prompt_embeds.shape == (
            1,
            prompt.shape[1],
            self.llama_model.text_model.config.hidden_size,
        ), f"Prompt shape is {prompt_embeds.shape}, expected {(1, prompt.shape[1], self.llama_model.text_model.config.hidden_size)}"
        embedded_bos = self.llama_model.text_model.model.embed_tokens(
            torch.tensor(
                [[self.llama_model.tokenizer.bos_token_id]],
                device=self.llama_model.text_model.device,
                dtype=torch.int64,
            )
        )

        # Construct prompts
        inputs_embeds = torch.cat(
            [
                embedded_bos.expand(embedded_images.shape[0], -1, -1),
                embedded_images.to(dtype=embedded_bos.dtype),
                prompt_embeds.expand(embedded_images.shape[0], -1, -1),
            ],
            dim=1,
        )

        input_ids = torch.cat(
            [
                torch.tensor(
                    [[self.llama_model.tokenizer.bos_token_id]], dtype=torch.long
                ),
                torch.zeros((1, embedded_images.shape[1]), dtype=torch.long),
                prompt,
            ],
            dim=1,
        ).to("cuda")
        attention_mask = torch.ones_like(input_ids)

        generate_ids = self.llama_model.text_model.generate(
            input_ids,
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=top_k,
            temperature=temperature,
            suppress_tokens=None,
        )

        # Trim off the prompt
        generate_ids = generate_ids[:, input_ids.shape[1] :]
        if generate_ids[0][-1] == self.llama_model.tokenizer.eos_token_id:
            generate_ids = generate_ids[:, :-1]

        caption = self.llama_model.tokenizer.batch_decode(
            generate_ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        )[0]
        print_log(f"Exec Finished")
        if clear_cache is True:
            self.clip_model = None
            self.llama_model = None

        return (caption.strip(),)

    def run_online(self, images):
        tmp_folder = os.path.join(config_data["base_path"], "tmp")
        if not os.path.exists(tmp_folder):
            os.mkdir(tmp_folder)

        try:
            for batch_number, image in enumerate(images):
                # 只处理一张
                i = 255.0 * image.cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
                file_name = f"{time.time()}_{create_nonceid(10)}.png"
                file_path = os.path.join(tmp_folder, file_name)
                img.save(file_path)
                break

            jco = joy_caption_online()
            result = jco.analyze(file_path).strip()

            os.remove(file_path)
        except Exception as e:
            print_log(f"删除临时文件失败：{e}")

        return (result,)

    def run(
        self,
        model,
        image,
        prompt,
        max_new_tokens,
        top_k,
        temperature,
        clear_cache,
        newbie,
    ):
        if newbie == True:
            return self.run_online(image)
        else:
            return self.run_local(
                model,
                image,
                prompt,
                max_new_tokens,
                top_k,
                temperature,
                clear_cache,
            )
