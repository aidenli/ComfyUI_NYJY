import json
from ..utils import print_log
from ..classes import AnyType
import re

any_type = AnyType("*")


class SplitString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("STRING", {"multiline": True}),
                "separator": ("STRING", {"default": ""}),
                "regex": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"
    OUTPUT_IS_LIST = (True, )

    def run(self, input, separator, regex):
        if regex:
            arr = re.split(separator, input)
        else:
            arr = input.split(separator)
        # 删除空行
        arr = [x for x in arr if x.strip() != ""]
        return (arr,)


class ConvertStringToNumber:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("STRING",),
            },
        }

    RETURN_TYPES = (
        "INT",
        "FLOAT",
    )
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, input):
        return (int(input), float(input))


class ConvertAnyToString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "obj": (any_type,),
            },
        }

    RETURN_TYPES = (
        "STRING",
    )
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, obj):
        try:
            # 使用 str() 函数将对象转换为字符串
            return (str(obj), )
        except Exception as e:
            # 如果转换失败，捕获异常并返回错误信息
            return ("", )


class ReadFileToString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "file_path": ("STRING", {"multiline": False}),
            },
        }

    RETURN_TYPES = (
        "STRING",
    )
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, file_path):
        try:
            # 打开文件并读取内容
            with open(file_path, 'r', encoding="utf-8") as file:
                content = file.read()
            return (content, )
        except Exception as e:
            # 如果读取失败，捕获异常并返回错误信息
            print_log("读取文件失败：" + str(e))
            return (str(e), )
