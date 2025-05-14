import pyaudio
import time
from xunfei_speech import XunfeiASR

def recognize_speech():
    asr = XunfeiASR()
    p = pyaudio.PyAudio()
    
    # 设置音频参数
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    print("正在初始化语音识别...")
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK)
    
    print("请说话...")
    try:
        # 启动讯飞语音识别
        asr.start_listening()
        
        # 录音5秒
        for i in range(0, int(RATE / CHUNK * 5)):
            data = stream.read(CHUNK)
            if not asr.is_listening:
                break
        
        # 停止录音和识别
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        text = asr.stop_listening()
        if text:
            print("识别结果: " + text)
            return text, None
        else:
            print("无法识别语音内容")
            return None, "无法识别语音内容"
            
    except Exception as e:
        print(f"发生未知错误: {e}")
        return None, f"发生未知错误: {e}"

if __name__ == '__main__':
    while True:
        result, error = recognize_speech()
        if result:
            print(f"\n成功识别: {result}")
        elif error:
            print(f"\n错误: {error}")
        
        time.sleep(1)  # 添加短暂延迟以防止CPU过度使用
        choice = input("\n是否继续语音识别？(y/n): ")
        if choice.lower() != 'y':
            break