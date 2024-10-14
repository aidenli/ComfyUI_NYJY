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
    packages = ["pygtrans", "fake_useragent", "lxml"]
    for package in packages:
        package_name = re.match(r"^([^\s=<>!]+)", package.strip())
        if package_name:
            install_package(package, package_name.group(1))


# 检查 requirements.txt 文件中的包
check_and_install_packages()


from .nodes.Translate import TranslateNode
from .nodes.JoyTag.JoyTag import JoyTagNode
from .nodes.JoyCaption.JoyCaption import JoyCaptionNode
from .nodes.JoyCaption.JoyCaption import JoyCaptionAlpha2OnlineNode
from .nodes.civitai_prompt import CivitaiPromptNode

NODE_CLASS_MAPPINGS = {
    "Translate": TranslateNode,
    "JoyTag": JoyTagNode,
    "JoyCaption": JoyCaptionNode,
    "JoyCaptionAlpha2Online": JoyCaptionAlpha2OnlineNode,
    "CivitaiPrompt": CivitaiPromptNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Translate": "Translate (NYJY)",
    "JoyTag": "JoyTag (NYJY)",
    "JoyCaption": "JoyCaption (NYJY)",
    "JoyCaptionAlpha2Online": "JoyCaptionAlpha2Online (NYJY)",
    "CivitaiPrompt": "CivitaiPrompt（NYJY）",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
