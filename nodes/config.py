import os
import json
from inspect import currentframe, stack, getmodule
import time

config_data = None
_base_path = None
_config_path = None
_template_path = None

def LoadConfig():
    global config_data, _base_path, _config_path, _template_path

    # 如果配置已加载，直接返回
    if config_data is not None:
        return config_data

    # 延迟初始化路径
    if _base_path is None:
        plugin_base_path = os.path.abspath(os.path.dirname(__file__))
        _template_path = os.path.join(plugin_base_path, "../config.json.template")
        _config_path = os.path.join(plugin_base_path, "../config.json")

    try:
        if os.path.exists(_config_path):
            with open(_config_path, "r", encoding='utf-8') as f:
                content = f.read()
                config_data = json.loads(content)
        else:
            print("config.json not found, use config.json.template")
            with open(_template_path, "r", encoding='utf-8') as f:
                content = f.read()
                config_data = json.loads(content)

        config_data["base_path"] = os.path.dirname(os.path.dirname(__file__))
        return config_data

    except FileNotFoundError as e:
        raise Exception(f"Configuration file not found: {e}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise Exception(f"Error loading configuration: {e}")
