import copy
from ..utils import print_log

PLATFORM_CONFIGS = {
    "bailian": {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "volcengine": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    },
    "common": {
        "base_url": "",
    }
}


def get_platform_config(platform):
    try:
        if platform not in PLATFORM_CONFIGS:
            raise ValueError(f"未找到平台 {platform} 的配置")

        platform_cfg = copy.deepcopy(PLATFORM_CONFIGS[platform])

        # 获取配置数据
        from ..config import config_data
        platform_cfg["api_key"] = config_data.get(platform, {}).get("Key", "")
        if platform_cfg["api_key"] == "":
            print_log(f"未在config.json中设置平台 {platform} 的Key")
        return platform_cfg
    except ImportError as e:
        print_log(str(e))
        return platform_cfg
    except Exception as e:
        raise ValueError(f"获取平台 {platform} 配置时出错: {str(e)}")


bailian_chat_models = [
    "qwq-plus",
    "qwq-32b",
    "qwen-max",
    "qwen-plus",
    "qwen-long",
    "deepseek-r1",
    "deepseek-v3",
    "deepseek-r1-distill-llama-70b",
    "deepseek-r1-distill-qwen-32b",
    "qwen-omni-turbo"
]

bailian_vl_models = [
    "qwen2.5-vl-72b-instruct",
    "qwen2.5-vl-7b-instruct",
    "qwen-vl-plus",
    "qwen-vl-max",
    "qvq-72b-preview",
    "qwen-omni-turbo"
]

bailian_i2v_models = [
    "wanx2.1-i2v-turbo",
    "wanx2.1-i2v-plus"
]