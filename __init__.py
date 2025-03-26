from .nodes.AIModelBridge.BridgeNode import BailianChatNode, BailianChatOption, BailianVLOption, BailianVLNode, CommonLLMChatNode
from .nodes.logics.strings_fn import SplitString, ConvertStringToNumber, ConvertAnyToString, ReadFileToString
from .nodes.logics.json_fn import JsonLoads, JsonDumps, JsonGetValueByKeys
from .nodes.logics.array_fn import GetItemFromList
from .nodes.number_tools import FloatSliderNode
from .nodes.image_tools import CustomLatentImageNode, CustomLatentImageSimpleNode
from .nodes.civitai_prompt import CivitaiPromptNode
from .nodes.JoyCaption.JoyCaption import (
    JoyCaptionAlpha2OnlineNode,
    JoyCaptionAlpha1OnlineNode,
)
from .nodes.JoyCaption.JoyCaption import JoyCaptionNode
from .nodes.JoyTag.JoyTag import JoyTagNode
from .nodes.Translate import TranslateNode
import importlib.util
import subprocess
import os
import re


def install_package(full_name, package_name):
    try:
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            raise ImportError(f"{package_name} 未安装")
    except ImportError:
        print(f"{package_name} 未安装，正在安装...")
        subprocess.check_call(["python", "-m", "pip", "install", full_name])
        print(f"{package_name} 安装完成。")


def check_and_install_packages():
    packages = ["pygtrans", "fake_useragent", "lxml", "openai"]
    for package in packages:
        package_name = re.match(r"^([^\s=<>!]+)", package.strip())
        if package_name:
            install_package(package, package_name.group(1))


# 检查 requirements.txt 文件中的包
# check_and_install_packages()


NODE_CLASS_MAPPINGS = {
    "Translate": TranslateNode,
    "JoyTag": JoyTagNode,
    "JoyCaption": JoyCaptionNode,
    "JoyCaptionAlpha2Online": JoyCaptionAlpha2OnlineNode,
    "JoyCaptionAlpha1Online": JoyCaptionAlpha1OnlineNode,
    "CivitaiPrompt": CivitaiPromptNode,
    "CustomLatentImage-NYJY": CustomLatentImageNode,
    "CustomLatentImageSimple": CustomLatentImageSimpleNode,
    "FloatSlider-NYJY": FloatSliderNode,
    "GetItemFromList": GetItemFromList,
    "JsonLoads": JsonLoads,
    "JsonDumps": JsonDumps,
    "JsonGetValueByKeys": JsonGetValueByKeys,
    "SplitString": SplitString,
    "ConvertStringToNumber": ConvertStringToNumber,
    "ConvertAnyToString": ConvertAnyToString,
    "ReadFileToString": ReadFileToString,
    "BailianChatOption": BailianChatOption,
    "BailianChat": BailianChatNode,
    "BailianVLOption": BailianVLOption,
    "BailianVL": BailianVLNode,
    "CommonLLMChat": CommonLLMChatNode,

}

NODE_DISPLAY_NAME_MAPPINGS = {}
for k in NODE_CLASS_MAPPINGS.keys():
    if "NYJY" in k:
        NODE_DISPLAY_NAME_MAPPINGS[k] = k
    else:
        NODE_DISPLAY_NAME_MAPPINGS[k] = k + "(NYJY)"

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS",
           "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
