from .type_tools import is_array
from ..classes import AnyType

any_type = AnyType("*")


class GetItemFromList:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "array": (any_type,),
                "index": ("INT", {"default": 0}),
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("item",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"
    OUTPUT_NODE = True

    def run(self, array, index):
        if is_array(array):
            if index[0] >= len(array):
                return {"ui": {"text": ("",)}, "result": ("",), }
            return {"ui": {"text": (array[index[0]],)}, "result": (array[index[0]],), }
        else:
            return {"ui": {"text": (array,)}, "result": (array,), }
