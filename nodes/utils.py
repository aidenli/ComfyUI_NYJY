import string
import secrets
import os
from .config import LoadConfig

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
    if winreg is None:
        config_data = LoadConfig()
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
                return None
        except FileNotFoundError:
            return None
