import time
from xunfei_speech import XunfeiTTS

def text_to_speech(text, rate=50, volume=50, voice_id=None):
    try:
        tts = XunfeiTTS()
        
        # 设置输出文件名
        output_file = 'temp_speech.wav'
        
        # 调用讯飞语音合成
        success, error = tts.text_to_speech(text, output_file)
        if success:
            return True, None
        else:
            return False, error
    except Exception as e:
        return False, f"语音合成出错: {e}"

if __name__ == '__main__':
    test_texts = [
        "你好，这是一个语音测试。",
        "我可以说中文和英文。Hello, I can speak both Chinese and English.",
        "让我们来测试一下语音合成的自然度和流畅性。"
    ]
    
    for text in test_texts:
        print(f"\n正在合成: {text}")
        success, error = text_to_speech(text)
        if not success:
            print(error)
        time.sleep(1)  # 测试间隔