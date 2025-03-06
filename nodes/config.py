import os
import json
from inspect import currentframe, stack, getmodule
import time

current_path = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(current_path, "../config.json")
config_data = {}

def LoadConfig():
    global config_data
    global config_path
    global current_path

    if config_data is not None:
        return config_data
    else:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                content = f.read()
                config_data = json.loads(content)
                
            current_dir = os.path.dirname(__file__)
            config_data["base_path"] = os.path.dirname(current_dir)
            return config_data
        return config_data


def print_log(str_msg):
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[NYJY][{str_time}][{stack()[1][1]}, line: {stack()[1][2]}]: {str_msg}")
