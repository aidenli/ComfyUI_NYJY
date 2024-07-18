# ComfyUI_NYJY
## 节点列表
### Translate -- 翻译节点，基于百度翻译接口，支持多语言

## 使用方法
### 修改配置
修改节点根目录下config.josn的内容
```
{
    "Baidu": {
        "AppId": "百度翻译平台的APPID",
        "Secret": "百度翻译平台的秘钥"
    }
}
```

### 获取百度翻译平台的APPID和秘钥
1. 登录百度翻译平台[ https://api.fanyi.baidu.com/manage/developer ]，在开发者中心可以获得个人的APPID和秘钥。
![alt text](docs/images/userinfo.png)

2. 访问[ https://api.fanyi.baidu.com/product/11 ]，开通“通用文本翻译API”。
![alt text](docs/images/api_service.png)

## 工作流示例（图片含工作流）
![alt text](docs/images/workflow-translate.png)
