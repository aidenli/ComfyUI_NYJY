import requests
import json
from pathlib import Path
from fake_useragent import UserAgent
from ..config import print_log
from ..utils import create_nonceid, get_system_proxy


class joy_caption_online:
    def __init__(self, host="fancyfeast-joy-caption-pre-alpha.hf.space") -> None:
        # 获取系统代理
        proxy = get_system_proxy()
        proxies = {
            "http": f"{proxy}",
            "https": f"{proxy}",
        }

        ua = UserAgent(platforms="pc")
        # 定义头部信息
        headers = {
            "origin": f"https://{host}",
            "referer": f"https://{host}/?__theme=light",
            "user-agent": ua.random,
        }

        self.__session = requests.Session()
        self.__session.trust_env = False
        self.__session.proxies = proxies
        self.__session.headers = headers
        self.__host = host
        pass

    def __upload_image(self, file_info):
        file_info.name
        nonceid = create_nonceid(11)

        try:
            response = self.__session.post(
                f"https://{self.__host}/upload?upload_id={nonceid}",
                files={"files": (file_info.name, open(file_info, "rb"))},
                timeout=20,
            )

            arr_img = json.loads(response.text)
            return arr_img[0]
        except requests.exceptions.RequestException as e:
            print_log(f"请求发生异常：{e}")
        except Exception as e:
            print_log(f"业务处理异常：{e}")
        return ""

    def __add_queue(self, img_url, file_info):
        nonceid = create_nonceid(10)
        try:
            response = self.__session.post(
                f"https://{self.__host}/queue/join?__theme=light",
                json={
                    "data": [
                        {
                            "path": img_url,
                            "url": f"https://{{self.__host}}/file={img_url}",
                            "orig_name": file_info.name,
                            "size": file_info.stat().st_size,
                            "mime_type": "image/jpeg",
                            "meta": {"_type": "gradio.FileData"},
                        }
                    ],
                    "event_data": None,
                    "fn_index": 0,
                    "trigger_id": 5,
                    "session_hash": nonceid,
                },
                timeout=60,
            )
            return nonceid
        except requests.exceptions.RequestException as e:
            print_log(f"请求发生异常：{e}")
        except Exception as e:
            print_log(f"业务处理异常：{e}")

        return ""

    def __get_result(self, nonceid):
        try:
            response = self.__session.get(
                f"https://{self.__host}/queue/data?session_hash={nonceid}",
                stream=True,
                timeout=30,
            )

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data:") == False:
                        continue

                    data = decoded_line[5:]
                    json_content = json.loads(data)

                    if json_content["msg"] != "process_completed":
                        continue

                    return json_content["output"]["data"][0]
        except requests.exceptions.RequestException as e:
            print_log(f"请求发生异常：{e}")
        except Exception as e:
            print_log(f"业务处理异常：{e}")

        return ""

    def analyze(self, img_path):
        file_info = Path(img_path)
        print_log("上传图片进行分析")
        img_url = self.__upload_image(file_info)
        if img_url == "":
            return ""
        print_log("提交服务器处理中...")
        nonceid = self.__add_queue(img_url, file_info)
        if nonceid == "":
            return ""
        print_log("图片分析中...")
        return self.__get_result(nonceid)
