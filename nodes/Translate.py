import os
import requests
import random
import json
from hashlib import md5
from .config import LoadConfig
from .utils import get_system_proxy
from pygtrans import Translate

# 语言列表
baidu_lang_list = {
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

google_lang_list = {
    "中文": "zh",
    "英语": "en",
    "日语": "ja",
    "韩语": "ko",
    "法语": "fr",
    "西班牙语": "es",
    "泰语": "th",
    "阿拉伯语": "ar",
    "俄语": "ru",
    "葡萄牙语": "pt",
    "德语": "de",
    "意大利语": "it",
    "希腊语": "el",
    "荷兰语": "nl",
    "波兰语": "pl",
    "保加利亚语": "bg",
    "爱沙尼亚语": "et",
    "丹麦语": "da",
    "芬兰语": "fi",
    "捷克语": "cs",
    "罗马尼亚语": "ro",
    "斯洛文尼亚语": "sl",
    "瑞典语": "sv",
    "匈牙利语": "hu",
    "繁体中文": "zh-TW",
    "越南语": "vi",
}


class TranslateNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "from_lang": (
                    ["自动"] + list(baidu_lang_list.keys()),
                    {"default": "自动"},
                ),
                "to_lang": (list(baidu_lang_list.keys()), {"default": "英语"}),
                "text": ("STRING", {"default": "", "multiline": True}),
                "platform": (["Google", "百度"], {"default": "百度"}),
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
    CATEGORY = "NYJY/text"

    def trans_by_baidu(self, from_lang, to_lang, text):
        endpoint = "http://api.fanyi.baidu.com"
        path = "/api/trans/vip/translate"
        url = endpoint + path

        query = " ".join(text.split("_"))

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
            "from": (
                baidu_lang_list[from_lang] if from_lang in baidu_lang_list else "auto"
            ),
            "to": baidu_lang_list[to_lang],
            "salt": salt,
            "sign": sign,
        }

        # Send request
        r = requests.post(url, params=payload, headers=headers, proxies=None)
        result = r.json()

        if "error_code" in result:
            print(f"[NYJY_Translate] exec translate failed：{json.dumps(result)}")
            return

        arr_res = []
        for item in result["trans_result"]:
            arr_res.append(item["dst"])

        return ("\n").join(arr_res)

    def trans_by_google(self, from_lang, to_lang, text):
        client = Translate(proxies={"https": self.proxy}, timeout=20)
        if from_lang == "自动":
            text = client.translate(text, target=google_lang_list[to_lang])
        else:
            text = client.translate(
                text,
                source=google_lang_list[from_lang],
                target=google_lang_list[to_lang],
            )

        return text.translatedText

    def run(self, from_lang, to_lang, text, platform, clip=None):
        config_data = LoadConfig()
        self.appid = config_data["Baidu"]["AppId"]
        self.appkey = config_data["Baidu"]["Secret"]
        self.proxy = get_system_proxy()

        if platform == "Google":
            translate_str = self.trans_by_google(from_lang, to_lang, text)
        else:
            translate_str = self.trans_by_baidu(from_lang, to_lang, text)

        if clip is None:
            return {
                "ui": {"text": (translate_str,)},
                "result": (
                    translate_str,
                    [[]],
                ),
            }

        tokens = clip.tokenize(translate_str)
        output = clip.encode_from_tokens(tokens, return_pooled=True, return_dict=True)
        cond = output.pop("cond")
        return {
            "ui": {"text": (translate_str,)},
            "result": (
                translate_str,
                [[cond, output]],
            ),
        }
