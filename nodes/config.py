import os
import json
from inspect import currentframe, stack, getmodule
import time


config_template = {
    "Baidu": {"AppId": "", "Secret": ""},
    "joytag": {
        "model_download": "https://hf-mirror.com/fancyfeast/joytag/tree/main",
        "hf_project": "fancyfeast/joytag",
    },
    "Google": {"proxy": ""},  # 代理地址，如：127.0.0.1:10809
    "DeepSeek": {
        "Key": ""
    }
}

current_path = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(current_path, "../config.json")
config_data = None


def merge_config(src_conf, target_conf):
    result = src_conf.copy()
    for key, value in target_conf.items():
        if key not in result:
            result[key] = value
        else:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_config(result[key], value)
    return result


def LoadConfig():
    global config_data
    global config_path
    global current_path

    if config_data is not None:
        return config_data
    else:
        config_data = config_template.copy()

        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                content = f.read()
                config_data = json.loads(content)
                # 合并最新的配置项（当config_template有变动的时候）
                config_data = merge_config(config_data, config_template)

        with open(config_path, "w") as f:
            f.write(json.dumps(config_data, indent=4))

        current_dir = os.path.dirname(__file__)
        config_data["base_path"] = os.path.dirname(current_dir)
        return config_data


def print_log(str_msg):
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[NYJY][{str_time}][{stack()[1][1]}, line: {stack()[1][2]}]: {str_msg}")
