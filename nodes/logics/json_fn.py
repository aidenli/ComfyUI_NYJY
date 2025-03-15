import json


class JsonLoads:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_data",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, text):
        try:
            print(text)
            json_data = json.loads(text)
            return {
                "result": (json_data,),
                "ui": {"text":  (text,)},
            }
        except json.JSONDecodeError:
            return {
                "result": ({},),
                "ui": {"text":  ("Invalid JSON format",)},
            }


class JsonDumps:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_data": ("JSON",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, json_data):
        text = json.dumps(json_data)
        return {
            "result": (text,),
            "ui": {"text":  (text,)},
        }


class JsonGetValueByKeys:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_data": ("JSON",),
                "key": ("STRING", {"default": "", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, json_data, key):
        # 校验 json_data 类型
        if not isinstance(json_data, (dict, list, tuple)):
            return ("",)

        keys = key.split(".")
        if not keys:
            return ("",)

        current_data = json_data

        empty_result = {
            "result": ("",),
            "ui": {"text":  ""},
        }
        for k in keys:
            # 处理数组索引
            try:
                if k.isdigit():  # 如果key是数字，尝试作为数组索引
                    index = int(k)
                    if isinstance(current_data, (list, tuple)):
                        if 0 <= index < len(current_data):  # 明确检查索引范围
                            current_data = current_data[index]
                            continue
                        else:
                            return empty_result
                # 处理字典
                if isinstance(current_data, dict):
                    if k not in current_data:
                        return empty_result
                    current_data = current_data[k]
                else:
                    return empty_result
            except (IndexError, KeyError, TypeError):
                return empty_result

        text = str(current_data)
        return {
            "result": (text,),
            "ui": {"text":  (text,)},
        }
