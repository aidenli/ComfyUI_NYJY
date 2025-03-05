import json


class JsonLoads:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("STRING", {"default": "", "multiline": True}),
            },
        }

    RETURN_TYPES = ("any_type",)
    RETURN_NAMES = ("json",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, input):
        return (json.loads(input),)


class JsonDumps:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_data": ("any_type",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, json_data):
        return (json.dumps(json_data),)
