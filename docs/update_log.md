## 更新日志
#### 2024-11-23
- 增加Joycaption One在线节点

#### 2024-10-25
- 增加了两个工具节点（CustomLatentImage-NYJY和FloatSlider-NYJY），感谢瓦里奥师兄提的需求。[使用方法](docs/images/CustomLatentImage-NYJY.png)

#### 2024-10-15
- 增加在线调用JoyCaption Alpha Two的节点，适合内存不足或者安装有困难的朋友体验，配额每日有上限（20次左右）
- 
#### 2024-09-24
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