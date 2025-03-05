import json
from ..classes import AnyType

any_type = AnyType("*")

class SplitString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("STRING",),
                "separator": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("listString",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"
    OUTPUT_IS_LIST = (True, )

    def run(self, input, separator):
        return (input.split(separator),)


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