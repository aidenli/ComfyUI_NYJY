import os
import requests
import random
import json
from hashlib import md5

current_path = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join(current_path, "../config.json")

# 语言列表
lang_list = {
    "中文": "zh",
    "英语": "en",
    "日语": "jp",
    "韩语": "kor",
    "法语": "fra",
    "西班牙语": "spa",
    "泰语": "th",
    "阿拉伯语": "ara",
    "俄语": "ru",
    "葡萄牙语": "pt",
    "德语": "de",
    "意大利语": "it",
    "希腊语": "el",
    "荷兰语": "nl",
    "波兰语": "pl",
    "保加利亚语": "bul",
    "爱沙尼亚语": "est",
    "丹麦语": "dan",
    "芬兰语": "fin",
    "捷克语": "cs",
    "罗马尼亚语": "rom",
    "斯洛文尼亚语": "slo",
    "瑞典语": "swe",
    "匈牙利语": "hu",
    "繁体中文": "cht",
    "越南语": "vie",
}


def read_config():
    config_data = {}
    try:
        with open(config_path, "r", encoding="utf-8") as fd:
            config_data = json.load(fd)
            appid = config_data["Baidu"]["AppId"]
            appkey = config_data["Baidu"]["Secret"]
            return (appid, appkey)
    except Exception as e:
        print(e)
    return ("", "")


class TranslateNode:
    def __init__(self):
        (appid, appkey) = read_config()
        self.appid = appid
        self.appkey = appkey
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "from_lang": (["自动"] + list(lang_list.keys()), {"default": "自动"}),
                "to_lang": (list(lang_list.keys()), {"default": "英语"}),
                "text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "clip": ("CLIP",),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "CONDITIONING",
    )
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "NYJY"

    def run(self, from_lang, to_lang, text, clip=None):
        endpoint = "http://api.fanyi.baidu.com"
        path = "/api/trans/vip/translate"
        url = endpoint + path

        query = text

        # Generate salt and sign
        def make_md5(s, encoding="utf-8"):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(self.appid + query + str(salt) + self.appkey)

        # Build request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "appid": self.appid,
            "q": query,
            "from": lang_list[from_lang],
            "to": lang_list[to_lang],
            "salt": salt,
            "sign": sign,
        }

        # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()

        if "error_code" in result:
            print(result)
            return

        translate_str = result["trans_result"][0]["dst"]
        print(result)
        if clip is None:
            return (translate_str, [[]])

        tokens = clip.tokenize(translate_str)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        return (
            translate_str,
            [[cond, {"pooled_output": pooled}]],
        )
