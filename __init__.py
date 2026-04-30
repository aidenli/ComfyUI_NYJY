from .nodes.AIModelBridge.bailian import BailianChatNode, BailianChatOption, BailianVLOption, BailianVLNode, CommonLLMChatNode
from .nodes.AIModelBridge.volcengine import VolcengineChatNode, VolcengineChatOption, VolcengineImageOption, VolcengineImg2ImgNode, VolcengineTxt2ImgNode,Seedream4Txt2ImgNode,Seedream4Img2ImgNode, Seedream3Txt2ImgNode, Seededit3Node, CreateSeedanceVideo
from .nodes.AIModelBridge.stepfun import StepFunTxt2ImgNode, StepFunImgEditNode
from .nodes.logics.strings_fn import SplitString, ConvertStringToNumber, ConvertAnyToString, ReadFileToString
from .nodes.logics.json_fn import JsonLoads, JsonDumps, JsonGetValueByKeys, JsonGetKeys
from .nodes.logics.array_fn import GetItemFromList, LengthOfArray
from .nodes.number_tools import FloatSliderNode, ConvertDenoseToStep
from .nodes.image_tools import CustomLatentImageNode, QwenLatentImageNode
from .nodes.civitai_prompt import CivitaiPromptNode
from .nodes.JoyCaption.JoyCaption import (
    JoyCaptionAlpha2OnlineNode,
    JoyCaptionAlpha1OnlineNode,
)
from .nodes.JoyCaption.JoyCaption import JoyCaptionNode
from .nodes.JoyTag.JoyTag import JoyTagNode
from .nodes.Translate import TranslateNode
from .nodes.fluxpro import FluxProOnlineNode

NODE_CLASS_MAPPINGS = {
    "LengthOfArray": LengthOfArray,
    "Translate": TranslateNode,
    "JoyTag": JoyTagNode,
    "JoyCaption": JoyCaptionNode,
    "JoyCaptionAlpha2Online": JoyCaptionAlpha2OnlineNode,
    "JoyCaptionAlpha1Online": JoyCaptionAlpha1OnlineNode,
    "CivitaiPrompt": CivitaiPromptNode,
    "CustomLatentImage-NYJY": CustomLatentImageNode,
    "FloatSlider-NYJY": FloatSliderNode,
    "GetItemFromList": GetItemFromList,
    "JsonLoads": JsonLoads,
    "JsonDumps": JsonDumps,
    "JsonGetValueByKeys": JsonGetValueByKeys,
    "JsonGetKeys":JsonGetKeys,
    "SplitString": SplitString,
    "ConvertStringToNumber": ConvertStringToNumber,
    "ConvertAnyToString": ConvertAnyToString,
    "ReadFileToString": ReadFileToString,
    "BailianChatOption": BailianChatOption,
    "BailianChat": BailianChatNode,
    "BailianVLOption": BailianVLOption,
    "BailianVL": BailianVLNode,
    "CommonLLMChat": CommonLLMChatNode,
    "FluxProOnline": FluxProOnlineNode,
    "QwenLatentImage": QwenLatentImageNode,
    "VolcengineChat": VolcengineChatNode,
    "VolcengineChatOption": VolcengineChatOption,
    "VolcengineImageOption": VolcengineImageOption,
    "VolcengineImg2Img": VolcengineImg2ImgNode,
    "VolcengineTxt2Img": VolcengineTxt2ImgNode,
    "Seedream4Txt2Img": Seedream4Txt2ImgNode,
    "Seedream4Img2Img": Seedream4Img2ImgNode,
    "Seedream3Txt2Img": Seedream3Txt2ImgNode,
    "Seededit3": Seededit3Node,
    "ConvertDenoseToStep": ConvertDenoseToStep,
    # "SeedanceVideo": SeedanceVideo,
    "CreateSeedanceVideo": CreateSeedanceVideo,
    "StepFunTxt2Img": StepFunTxt2ImgNode,
    "StepFunImgEdit": StepFunImgEditNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {}
for k in NODE_CLASS_MAPPINGS.keys():
    if "NYJY" in k:
        NODE_DISPLAY_NAME_MAPPINGS[k] = k
    else:
        NODE_DISPLAY_NAME_MAPPINGS[k] = k + "(NYJY)"

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS",
           "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
