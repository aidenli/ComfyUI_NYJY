# ComfyUI_NYJY
## 更新日志
#### 2024-09-124
- 修改JoyTag依赖模型的路径为 models/clip/joytag
- 运行CivitaiPrompt获取图片提示词后，会将图片和提示词记录在 output/civitai_prompt目录中
  
#### 2024-09-13
- 增加CivitaiPrompt节点
- 修复一些bug，优化体验

（感谢王剑锋老师提出的修改建议）

#### 2024-09-01
- 支持Google翻译。更新的小伙伴需要安装一个新的包：pygtrans。
```bash
[comfyui根目录]\python_embeded\python.exe -m pip install pygtrans
```

#### 2024-08-20
- 增加JoyCaption节点（joy-caption项目地址：https://huggingface.co/spaces/fancyfeast/joy-caption-pre-alpha ）

#### 2024-08-14
- 解决了模型重复下载问题
- joytag增加了安全模式和自定义tag
- 修复了百度翻译中对于带下划线的词无法翻译的问题

（感谢艾威大师兄提出的修改建议）

## 节点列表
#### [Translate -- 翻译节点，对接谷歌翻译和百度翻译，支持多语言。（点击查看详细）](docs/translate.md)

#### [JoyTag -- 反推图片，输出tags。（点击查看详细）](docs/joytag.md)

#### [JoyCaption -- 反推图片，输出自然语言。（点击查看详细）](docs/joycaption.md)

#### [CivitaiPrompt -- 随机获取C站图片的提示词。（点击查看详细）](docs/civitaiprompt.md)

## 安装方法（两种方式）
### 1. 通过ComfyUI Manager安装。

打开ComfyUI Manager，点击“Install via Git URL”按钮

在弹出的对话框中填入：https://github.com/aidenli/ComfyUI_NYJY

![安装](docs/images/install.jpg)

### 2. 手动拷贝
访问项目地址：https://github.com/aidenli/ComfyUI_NYJY
点击Code按钮，在弹出的浮层中点击“Download ZIP”。下载后解压到 [你的ConmfyUI目录]/custom_nodes/

![安装](docs/images/install-2.jpg)
