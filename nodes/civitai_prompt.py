import requests
from fake_useragent import UserAgent
import json
from urllib.parse import quote
import random
from .utils import get_system_proxy
from lxml import html
from .utils import print_log, save_image_bytes_for_preview
import urllib.request
import folder_paths
import os


class CivitaiPromptNode:
    __session = None
    __image_list = []
    __next_cursor = None
    __cache_id = None
    __cache_positive = ""
    __cache_negative = ""
    __cache_previews = []

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "fixed_prompt": ("BOOLEAN", {"default": True}),
                "preview_image": ("BOOLEAN", {"default": True}),
                "mirror_sites": ("BOOLEAN", {"default": False}),
            },
        }

    @classmethod
    def IS_CHANGED(self, fixed_prompt, preview_image, mirror_sites):
        if fixed_prompt:
            return self.__cache_id
        else:
            return random.random()

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "choise_image"
    OUTPUT_NODE = False
    CATEGORY = "NYJY/text"

    def init_request(self, mirror_sites):
        self.__session = requests.Session()

        if mirror_sites == True:
            host = "civitai.work"
        else:
            host = "civitai.com"

            proxy = get_system_proxy()
            if proxy is not None:
                proxies = {
                    "http": f"{proxy}",
                    "https": f"{proxy}",
                }
                self.__session.trust_env = False
                self.__session.proxies = proxies

        ua = UserAgent(platforms="pc")
        self.__host = host
        self.__session.headers = {
            "origin": f"https://{host}",
            "referer": f"https://{host}",
            "user-agent": ua.random,
        }

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
            req = f"https://{self.__host}/api/trpc/image.getInfinite?input={quote(json.dumps(req_data))}"
            response = self.__session.get(req, timeout=10)

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

    def get_image_detail(self, image_id) -> tuple[str, str, int]:
        req_data = {"json": {"id": image_id}}

        try:
            response = self.__session.get(
                f"https://{self.__host}/api/trpc/image.getGenerationData?input={quote(json.dumps(req_data))}",
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
                0,
            )

        except Exception as e:
            print_log(f"获取图片详情失败[{image_id}]:{e}")
            return ("", "", 1)

    def get_image(self, image_id):
        try:
            response = self.__session.get(
                f"https://{self.__host}/images/{image_id}", timeout=10
            )
            tree = html.fromstring(response.text)
            results = tree.xpath(
                "//div[contains(@class,'mantine-Carousel-slide')]//img[1]/@src"
            )
            if len(results) > 0:
                img_url = results[0].replace("original=true", "width=450")
                print_log(f"下载图片: {img_url}")
                img_response = self.__session.get(img_url, timeout=20)
                if img_response.status_code == 200:
                    return img_response.content
            return None
        except Exception as e:
            print_log(f"下载图片失败[{image_id}]:{e}")
            return []

    def choise_image(
        self, fixed_prompt, preview_image, mirror_sites
    ) -> tuple[str, str]:
        self.init_request(mirror_sites)
        previews = []

        if len(self.__image_list) < 10:
            print_log(f"获取图片列表")
            self.__image_list += self.req_list(self.__next_cursor)

        # 如果是保持提示词并且有缓存的图片id，则使用缓存图片id的数据
        if fixed_prompt and self.__cache_id is not None:
            print_log(f"load cache")
            return {
                "result": (self.__cache_positive, self.__cache_negative),
                "ui": {"images": self.__cache_previews},
            }

        if len(self.__image_list) == 0:
            return {"result": ("", ""), "ui": {"images": previews}}

        cur = 0
        while cur < 5:
            cur += 1
            idx = random.randint(0, len(self.__image_list) - 1)
            image_id = self.__image_list.pop(idx)
            print_log(f"获取图片[{image_id}]的提示词")
            positive, negative, errcode = self.get_image_detail(image_id)
            if errcode > 0:
                break

            if len(positive) > 0:
                self.__cache_id = image_id
                self.__cache_positive = positive
                self.__cache_negative = negative
                if preview_image:
                    print_log(f"获取图片[{image_id}]的内容")
                    image_content = self.get_image(image_id)

                    output_dir = os.path.join(
                        folder_paths.get_output_directory(), "civitai_prompt"
                    )

                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    # 保存图片到output目录
                    with open(os.path.join(output_dir, f"{image_id}.jpeg"), "wb") as f:
                        f.write(image_content)
                    # 保存提示词
                    with open(
                        os.path.join(output_dir, f"{image_id}_prmopt.txt"), "w"
                    ) as f:
                        f.write(f"positive:\n{positive}")
                        if len(negative) > 0:
                            f.write(f"\n\n---------------------\nnegative:\n{negative}")

                    previews = [save_image_bytes_for_preview(image_content)]
                    self.__cache_previews = previews
                return {"result": (positive, negative), "ui": {"images": previews}}

        return {"result": ("", ""), "ui": {"images": previews}}
