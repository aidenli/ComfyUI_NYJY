### 使用说明
#### 1 JoyTag基本信息
原项目github地址：https://github.com/fpgaminer/joytag

该插件运行时会自动下载所需的模型，下载模型的所有相关文件将存放到：[comfyui根目录]/costom_nodes/ComfyUI_NYJY/models/joytag中。

如果使用手动下载，需要自己创建目录。模型下载地址：https://huggingface.co/fancyfeast/joytag/tree/main （model.onnx文件可以不用下载）

#### 2 节点参数说明

THRESHOLD：浮点类型，范围 0.1 - 1，值越小，产生的tag数量越多。

正面提示词：在完成分析图片之后，额外自定义添加到tag列表的词或句子

负面提示词：在完成缝隙图片之后，需要过滤掉的tag

safe_mode：安全模式，自动过滤tag中血腥、色情等提示词（词库逐步完善中）

#### 3 工作流示例（图片含工作流）

![alt text](images/image1.png)

感谢WARIO WORLD提供的图片

![alt text](images/workflow-joytag.png)
