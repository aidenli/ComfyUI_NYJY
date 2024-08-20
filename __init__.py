from .nodes.Translate import TranslateNode
from .nodes.JoyTag.JoyTag import JoyTagNode
from .nodes.JoyCaption.JoyCaption import JoyCaptionNode

NODE_CLASS_MAPPINGS = {
    "Translate": TranslateNode,
    "JoyTag": JoyTagNode,
    # "LoadLlamaModel": LoadLlamaModelNode,
    "JoyCaption": JoyCaptionNode,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "Translate": "Translate (NYJY)",
    "JoyTag": "JoyTag (NYJY)",
    # "LoadLlamaModel": "LoadLlamaModel (NYJY)",
    "JoyCaption": "JoyCaption (NYJY)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
