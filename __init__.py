from .nodes.Translate import TranslateNode
from .nodes.JoyTag.JoyTag import JoyTagNode

NODE_CLASS_MAPPINGS = {"Translate": TranslateNode, "JoyTag": JoyTagNode}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Translate": "Translate（NYJY）",
    "JoyTag": "JoyTag（NYJY）",
}
