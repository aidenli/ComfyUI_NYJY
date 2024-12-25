from .type_tools import is_array
from ..utils import AnyType

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

    RETURN_TYPES = ("any_type",)
    RETURN_NAMES = ("result",)
    FUNCTION = "run"
    CATEGORY = "NYJY/logic"

    def run(self, array, index):
        if is_array(array):
            if index >= len(array):
                return None
            return array[index]