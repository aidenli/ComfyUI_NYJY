import string
import secrets
import winreg


def create_nonceid(length=10):
    alphabet = string.ascii_letters + string.digits
    nonceid = "".join(secrets.choice(alphabet) for i in range(length))
    return nonceid


# 获取系统代理地址
def get_system_proxy():
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