## 使用说明
#### 0 翻译平台说明
节点提供了两个翻译平台：Google和百度。

如果选择Google翻译，只需要保持梯子通畅即可使用；

如果选择百度翻译，请继续按照以下“修改配置”和“获取百度翻译平台的APPID和秘钥”步骤操作

#### 1 修改配置
修根目录下config.josn的内容（如果没有config.json，则手动创建一个），路径为：ComfyUI_NYJY
```
{
    "Baidu": {
        "AppId": "百度翻译平台的APPID",
        "Secret": "百度翻译平台的秘钥"
    }
}
```

#### 2 获取百度翻译平台的APPID和秘钥
(1) 登录百度翻译平台[ https://api.fanyi.baidu.com/manage/developer ]，在开发者中心可以获得个人的APPID和秘钥。
![alt text](images/userinfo.png)

(2) 访问[ https://api.fanyi.baidu.com/product/11 ]，开通“通用文本翻译API”。
![alt text](images/api_service.png)

#### 3 工作流示例（图片含工作流）
![alt text](images/workflow-translate.png)