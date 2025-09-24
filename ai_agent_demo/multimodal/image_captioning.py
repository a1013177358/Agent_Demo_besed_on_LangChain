# -*- coding: utf-8 -*-
"""
@File    : image_captioning.py
@Time    : 2025/9/25 15:20
@Desc    : 图像描述生成模块，用于将图像内容转换为文本描述 
"""
import time
# 从transformers库导入BlipProcessor和BlipForConditionalGeneration类
from transformers import BlipProcessor, BlipForConditionalGeneration
# 从Pillow库导入Image类，用于处理图像
from PIL import Image

# 全局变量，用于缓存模型和处理器
_processor = None
_model = None

# 模型名称常量
MODEL_NAME = "Salesforce/blip-image-captioning-base"

def _load_model_if_needed():
    """
    懒加载模型和处理器，只在首次调用时加载
    """
    global _processor, _model
    if _processor is None or _model is None:
        start_time = time.time()
        print(f"加载图像描述生成模型: {MODEL_NAME}")
        # 从预训练模型加载BlipProcessor
        _processor = BlipProcessor.from_pretrained(MODEL_NAME)
        # 从预训练模型加载BlipForConditionalGeneration
        _model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME)
        print(f"图像描述生成模型加载完成，耗时: {time.time() - start_time:.2f}秒")

# 定义一个函数，用于为指定路径的图像生成字幕
# 参数 image_path: 图像文件的路径，类型为字符串
# 返回值: 生成的图像字幕，类型为字符串
def caption_image(image_path: str) -> str:
    # 确保模型已加载
    _load_model_if_needed()
    
    # 打开指定路径的图像文件，并将其转换为RGB格式
    image = Image.open(image_path).convert("RGB")
    # 使用processor对图像进行处理，转换为PyTorch张量
    inputs = _processor(images=image, return_tensors="pt")
    # 使用模型生成图像的字幕，最多生成50个新token
    output = _model.generate(**inputs, max_new_tokens=50)
    # 对模型输出进行解码，跳过特殊token，得到最终的字幕文本
    caption = _processor.decode(output[0], skip_special_tokens=True)
    return caption

if __name__ == '__main__':
    # 调用caption_image函数，为指定路径的图像生成字幕
    result = caption_image("Agent Demo/ai_agent_demo/data/Surfing_in_Hawaii.png")
    # 打印生成的字幕，示例输出为 "a man riding a wave on a surfboard"
    print(result)  # a man riding a wave on a surfboard
