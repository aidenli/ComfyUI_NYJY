# ComfyUI_NYJY
## 更新日志
#### 2024-08-20
- 增加JoyCaption节点（joy-caption项目地址：https://huggingface.co/spaces/fancyfeast/joy-caption-pre-alpha ）

#### 2024-08-14
- 解决了模型重复下载问题
- joytag增加了安全模式和自定义tag
- 修复了百度翻译中对于带下划线的词无法翻译的问题

（感谢艾威大师兄提出的修改建议）

## 节点列表
#### [Translate -- 翻译节点，基于百度翻译接口，支持多语言](docs/translate.md)

#### [JoyTag -- 反推图片，输出tags](docs/joytag.md)

#### [JoyCaption -- 反推图片，输出自然语言](docs/joycaption.md)

## 安装方法（两种方式）
### 1. 通过ComfyUI Manager安装。

打开ComfyUI Manager，点击“Install via Git URL”按钮

在弹出的对话框中填入：https://github.com/aidenli/ComfyUI_NYJY

![安装](docs/images/install.jpg)

### 2. 手动拷贝
访问项目地址：https://github.com/aidenli/ComfyUI_NYJY
点击Code按钮，在弹出的浮层中点击“Download ZIP”。下载后解压到 [你的ConmfyUI目录]/custom_nodes/

![安装](docs/images/install-2.jpg)