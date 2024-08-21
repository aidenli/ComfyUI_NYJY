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
    "Translate": "Translate[文本翻译] (NYJY)",
    "JoyTag": "JoyTag[图片反推，输出Tags] (NYJY)",
    # "LoadLlamaModel": "LoadLlamaModel (NYJY)",
    "JoyCaption": "JoyCaption[图片反推，输出自然语言] (NYJY)",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
