import json


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

    def run(self, input, separator):
        return input.split(separator)


class ConverAnyToString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input": ("any_type",),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, input):
        return json.loads(input)


class ConverStringToNumber:
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
