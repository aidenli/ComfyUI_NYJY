import string
import secrets
import os
from .config import LoadConfig
import random
import folder_paths
from inspect import currentframe, stack, getmodule
import time
import requests

# Import winreg only if running on Windows
if os.name == "nt":  # 'nt' indicates Windows
    import winreg
else:
    # Define a mock for winreg to avoid errors on non-Windows platforms
    winreg = None


def create_nonceid(length=10):
    alphabet = string.ascii_letters + string.digits
    nonceid = "".join(secrets.choice(alphabet) for i in range(length))
    return nonceid


# 获取系统代理地址
def get_system_proxy():
    config_data = LoadConfig()
    if winreg is None:
        return config_data["Google"]["proxy"] if "Google" in config_data else None
    else:
        try:
            internet_settings = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            )
            proxy_server, _ = winreg.QueryValueEx(internet_settings, "ProxyServer")
            proxy_enable, _ = winreg.QueryValueEx(internet_settings, "ProxyEnable")
            if proxy_enable:
                return proxy_server
            else:
                print_log("没有查询到系统的代理")
                return None
        except FileNotFoundError:
            print_log("没有查询到系统的代理")
            return None


def save_image_bytes_for_preview(image, output_dir: str = None, prefix=None):
    if output_dir is None:
        output_dir = folder_paths.get_temp_directory()

    if prefix is None:
        prefix = "preview_" + "".join(
            random.choice("abcdefghijklmnopqrstupvxyz") for x in range(8)
        )

    # save image to temp folder
    (
        outdir,
        filename,
        counter,
        subfolder,
        _,
    ) = folder_paths.get_save_image_path(prefix, output_dir)
    file = f"{filename}_{counter:05}_.jpeg"
    with open(os.path.join(outdir, file), "wb") as f:
        f.write(image)
    print_log(
        {
            "filename": file,
            "subfolder": subfolder,
            "type": "temp",
        }
    )
    return {
        "filename": file,
        "subfolder": subfolder,
        "type": "temp",
    }


def print_log(str_msg):
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[NYJY][{str_time}][{stack()[1][1]}, line: {stack()[1][2]}]: {str_msg}")


class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")
