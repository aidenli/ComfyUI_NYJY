from AIModelBridge.api import *

# 测试代码示例
if __name__ == "__main__":
    # 创建工厂实例
    factory = AIModelBridgeFactory()

    # 测试百炼模型
    bailian_model = factory.get_model("bailian")

    bailian_model.set_config(
        {"api_key": "sk-b07a372fef9840bebcaf0a2551feb941"})
    messages = [
        {"role": "system", "content": "你是一个AI助手"},
        {"role": "user", "content": "你好"}
    ]
    try:
        bailian_response = bailian_model.chat_completion(
            model="deepseek-r11",
            messages=messages
        )
        print("百炼响应:", bailian_response.choices[0].message.content)
    except Exception as e:
        print("百炼测试失败:", e)

    # 测试火山引擎模型
    volcengine_model = factory.get_model("volcengine")
    volcengine_model.set_config(
        {"api_key": "27092347-6c4c-49a8-afa4-7ace57fc4d9a"})
    try:
        volcengine_response = volcengine_model.chat_completion(
            model="deepseek-r1-distill-qwen-7b-250120",
            messages=messages
        )
        print("火山引擎响应:", volcengine_response.choices[0].message.content)
    except Exception as e:
        print("火山引擎测试失败:", e)
