## 使用说明
#### 0 翻译平台说明
节点提供了两个翻译平台：Google和百度。

如果选择Google翻译，只需要保持梯子通畅即可使用；

如果选择百度翻译，请继续按照以下“修改配置”和“获取百度翻译平台的APPID和秘钥”步骤操作

#### 1 修改配置
将根目录下config.josn.template文件重命名为config.json（或者新建一个文件也可以），修改以下内容：
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

(3) 修改ComfyUI_NYJY/config.json的内容
```
{
    "Baidu": {
        "AppId": "百度翻译平台的APPID",
        "Secret": "百度翻译平台的秘钥"
    }
}
```

#### 4 设置DeepSeek的key
(1) 登录DeepSeek，在API Keys页面[https://platform.deepseek.com/api_keys]中创建一个key，也可以用现有的
![alt text](images/DeepSeekApi.png)

(2) 修改ComfyUI_NYJY/config.json的内容
```
{
    "DeepSeek": {
        "Key": "sk-xxxxx"
    }
}
```
#### 3 工作流示例（图片含工作流）
![alt text](images/workflow-translate.png)

