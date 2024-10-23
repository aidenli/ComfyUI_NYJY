import math


class FloatSliderNode:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "number": (
                    "FLOAT",
                    {
                        "display": "slider",
                        "default": 1.0,
                        # "min": 0,
                        "step": 0.1,
                        "precision": 1,
                    },
                ),
                "min_value": (
                    "FLOAT",
                    {
                        "default": 0,
                        "step": 0.1,
                        "precision": 1,
                    },
                ),
                "max_value": (
                    "FLOAT",
                    {
                        "default": 1,
                        "step": 0.1,
                        "precision": 1,
                    },
                ),
                "precision": (
                    ["1", "0.1", "0.01", "0.001"],
                    {"default": "0.1"},
                ),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT")
    FUNCTION = "run"
    OUTPUT_NODE = True
    CATEGORY = "NYJY"

    def run(self, number, min_value, max_value, precision):
        print(number)
        nResult = math.ceil(number)
        match precision:
            case "1":
                fResult = math.ceil(number)
            case "0.1":
                fResult = round(number, 1)
            case "0.01":
                fResult = round(number, 2)
            case "0.001":
                fResult = round(number, 3)

        return {"result": (fResult, nResult)}
