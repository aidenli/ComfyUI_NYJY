import requests
from fake_useragent import UserAgent
import json
from urllib.parse import quote
import random
from .utils import get_system_proxy
from lxml import html
from .utils import save_image_bytes_for_preview, print_log


class CivitaiPromptNode:
    __image_list = []
    __next_cursor = None
    __selected_image_id = None
    __cache_id = None

    def __init__(self, host="civitai.com", max_page=3):
        proxy = get_system_proxy()
        proxies = {
            "http": f"{proxy}",
            "https": f"{proxy}",
        }

        ua = UserAgent(platforms="pc")
        # 定义头部信息
        headers = {
            "origin": f"https://{host}",
            "referer": f"https://{host}",
            "user-agent": ua.random,
        }

        self.__session = requests.Session()
        self.__session.trust_env = False
        self.__session.proxies = proxies
        self.__session.headers = headers
        self._max_page = max_page

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"fixed_prompt": ("BOOLEAN", {"default": True})},
        }

    @classmethod
    def IS_CHANGED(self, fixed_prompt):
        if fixed_prompt:
            return self.__cache_id
        else:
            return random.random()

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "choise_image"
    OUTPUT_NODE = False
    CATEGORY = "NYJY/text"

    def req_list(self, next_cursor=None):
        if next_cursor is None:
            req_data = {
                "json": {
                    "useIndex": True,
                    "period": "Day",
                    "sort": "Most Reactions",
                    "types": ["image"],
                    "withMeta": False,
                    "browsingLevel": 1,
                    "include": ["cosmetics"],
                    "cursor": None,
                },
                "meta": {"values": {"cursor": ["undefined"]}},
            }
        else:
            req_data = {
                "json": {
                    "useIndex": True,
                    "period": "Day",
                    "sort": "Most Reactions",
                    "types": ["image"],
                    "withMeta": False,
                    "browsingLevel": 1,
                    "include": ["cosmetics"],
                    "cursor": next_cursor,
                }
            }

        try:
            req = f"https://civitai.com/api/trpc/image.getInfinite?input={quote(json.dumps(req_data))}"
            response = self.__session.get(req, timeout=20)

            json_rsp = json.loads(response.text)

            def filter_meta(item):
                if item["hideMeta"] == True or item["hasMeta"] == False:
                    return False
                else:
                    return True

            self.__next_cursor = json_rsp["result"]["data"]["json"]["nextCursor"]
            return [
                item["id"]
                for item in json_rsp["result"]["data"]["json"]["items"]
                if filter_meta(item)
            ]
        except Exception as e:
            print_log(f"获取图片列表失败:{e}")
            return []

    def get_image_detail(self, image_id) -> tuple[str, str]:
        req_data = {"json": {"id": image_id}}

        try:
            response = self.__session.get(
                f"https://civitai.com/api/trpc/image.getGenerationData?input={quote(json.dumps(req_data))}",
                timeout=10,
            )

            json_rsp = json.loads(response.text)
            return (
                (
                    json_rsp["result"]["data"]["json"]["meta"]["prompt"]
                    if "prompt" in json_rsp["result"]["data"]["json"]["meta"]
                    else ""
                ),
                (
                    json_rsp["result"]["data"]["json"]["meta"]["negativePrompt"]
                    if "negativePrompt" in json_rsp["result"]["data"]["json"]["meta"]
                    else ""
                ),
            )

        except Exception as e:
            print_log(f"获取图片详情失败[{image_id}]:{e}")
            return ("", "")

    def get_image(self, image_id):
        try:
            response = self.__session.get(
                f"https://civitai.com/images/{image_id}", timeout=10
            )
            tree = html.fromstring(response.text)
            results = tree.xpath(
                "//div[contains(@class,'mantine-Carousel-slide')]//img[1]/@src"
            )

            img_response = self.__session.get(results[0])
            if img_response.status_code == 200:
                return [
                    save_image_bytes_for_preview(
                        img_response.content, None, f"cimage_{image_id}"
                    )
                ]

            return []
        except Exception as e:
            print_log(f"下载图片失败[{image_id}]:{e}")
            return []

    def choise_image(self, fixed_prompt) -> tuple[str, str]:
        previews = []

        if len(self.__image_list) < 10:
            print_log(f"获取图片列表")
            self.__image_list += self.req_list(self.__next_cursor)

        # 如果是保持提示词并且有缓存的图片id，则使用缓存图片id的数据
        if fixed_prompt and self.__cache_id is not None:
            positive, negative = self.get_image_detail(self.__cache_id)
            previews = self.get_image(self.__cache_id)
            return {"result": (positive, negative), "ui": {"images": previews}}

        cur = 0
        while cur < 5:
            cur += 1
            idx = random.randint(0, len(self.__image_list) - 1)
            image_id = self.__image_list.pop(idx)
            print_log(f"获取图片[{image_id}]的提示词")

            positive, negative = self.get_image_detail(image_id)
            if len(positive) > 0:
                self.__cache_id = image_id
                previews = self.get_image(image_id)
                print_log(f"获取图片[{image_id}]的内容")
                return {"result": (positive, negative), "ui": {"images": previews}}

        return {"result": ("", ""), "ui": {"images": previews}}
