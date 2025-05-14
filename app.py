import sys
import os
import streamlit as st
import warnings
import asyncio
import platform
import speech_recognition as sr
import pyttsx3
from PIL import Image
import io
import base64
from datetime import datetime

# 设置环境变量
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_WEB_SOCKET_CONNECTION'] = 'false'
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'true'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# 预处理torch.classes
if 'torch.classes' in sys.modules:
    del sys.modules['torch.classes']

class FakePath:
    _path = []

class FakeClasses:
    __path__ = FakePath()

if 'torch' in sys.modules and not hasattr(sys.modules['torch'], 'classes'):
    sys.modules['torch'].classes = FakeClasses()
if 'torch.classes' not in sys.modules:
    sys.modules['torch.classes'] = FakeClasses()

# 忽略警告
warnings.filterwarnings("ignore", category=RuntimeWarning)

# 导入自定义工具
from utils import generate_response, select_model, detect_language, emotional_response, model_manager

# 增强事件循环处理
if platform.system() == "Windows":
    if hasattr(asyncio, 'WindowsProactorEventLoopPolicy'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# 页面配置
st.set_page_config(
    page_title="智能聊天助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.stApp {
    background-color: #f8f9fa;
}
.chat-message {
    padding: 1.5rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    max-width: 85%;
}
.user-message {
    background-color: #e3f2fd;
    margin-left: auto;
    border-bottom-right-radius: 0.2rem;
}
.assistant-message {
    background-color: #f3e5f5;
    border-bottom-left-radius: 0.2rem;
}
.system-message {
    background-color: #f5f5f5;
    font-style: italic;
    text-align: center;
    max-width: 100%;
}
.model-status {
    padding: 0.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    background-color: #e8f5e9;
}
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "system",
        "content": "👋 欢迎使用智能聊天助手！我可以帮您解答问题、编写代码、分析图片等。",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

if 'current_model' not in st.session_state:
    st.session_state.current_model = 'qwen2'

if 'model_params' not in st.session_state:
    st.session_state.model_params = {
        'temperature': 0.7,
        'top_p': 0.9,
        'max_tokens': 2048
    }

# 侧边栏配置
with st.sidebar:
    st.title("⚙️ 系统设置")
    
    # 基础设置
    st.subheader("🌍 基础设置")
    language = st.selectbox(
        "界面语言",
        ["中文", "English", "日本語", "한국어"],
        help="选择界面显示语言"
    )
    
    # 模型设置
    st.subheader("🎯 模型设置")
    model_mode = st.radio(
        "模型选择模式",
        ["自动选择", "手动选择"],
        help="自动模式将根据输入内容智能选择合适的模型"
    )
    
    if model_mode == "手动选择":
        st.session_state.current_model = st.selectbox(
            "选择模型",
            list(model_manager.models.keys()),
            help="选择要使用的AI模型"
        )
        
        # 模型参数调整
        st.session_state.model_params['temperature'] = st.slider(
            "温度 (Temperature)",
            0.0, 1.0, st.session_state.model_params['temperature'],
            help="控制回答的创造性，值越大回答越多样化"
        )
        st.session_state.model_params['top_p'] = st.slider(
            "采样阈值 (Top P)",
            0.0, 1.0, st.session_state.model_params['top_p'],
            help="控制回答的质量，值越小回答越保守"
        )
    
    # 功能设置
    st.subheader("🎨 功能设置")
    enable_emotion = st.toggle("启用情感交互", value=True, help="开启后AI会理解并回应情感")
    enable_voice = st.toggle("启用语音交互", value=True, help="开启后可以使用语音输入和播报")
    enable_image = st.toggle("启用图片分析", value=True, help="开启后可以上传图片进行分析")
    
    # 系统状态
    st.subheader("📊 系统状态")
    st.info(f"当前模型: {st.session_state.current_model}")
    st.info(f"会话数量: {len(st.session_state.messages)}")
    
    # 清空会话
    if st.button("🗑️ 清空会话记录"):
        st.session_state.messages = [st.session_state.messages[0]]  # 保留系统欢迎消息
        st.success("会话已清空")

# 主界面
st.title("🤖 智能聊天助手")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"{message['content']}")
        st.caption(f"时间: {message.get('timestamp', '')}")

# 图片上传功能
if enable_image:
    uploaded_file = st.file_uploader("上传图片进行分析", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="上传的图片", use_column_width=True)
        prompt = f"请分析这张图片的内容和特点"
        
        with st.spinner("正在分析图片..."):
            response = generate_response(prompt, st.session_state.current_model)
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": timestamp
            })
            with st.chat_message("assistant"):
                st.markdown(response)
                st.caption(f"时间: {timestamp}")

# 语音识别
def recognize_speech():
    r = sr.Recognizer()
    max_retries = 3
    
    try:
        with sr.Microphone() as source:
            st.write("请说话...")
            st.write("正在录音...")
            # 调整麦克风参数以提高识别率
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            st.write("录音完成，正在识别...")
        
        # 修改识别服务的优先级，优先使用讯飞语音识别
        from xunfei_speech import recognize_with_xunfei
        try:
            # 1. 优先使用讯飞语音识别
            result = recognize_with_xunfei(audio.get_raw_data())
            if result:
                return result
        except Exception as e:
            st.warning(f"讯飞语音识别失败: {str(e)}")

        # 2. 备选识别服务
        recognition_services = [
            lambda: try_google_recognition(r, audio, max_retries),
            lambda: try_sphinx_recognition(r, audio),
            lambda: try_other_recognition(r, audio)
        ]
        
        # 依次尝试各种识别服务
        for service in recognition_services:
            try:
                result = service()
                if result:
                    return result
            except Exception as e:
                st.warning(f"识别服务尝试失败: {str(e)}")
                continue
        
        # 如果所有服务都失败，提供手动输入选项
        st.error("所有语音识别服务均不可用")
        manual_input = st.text_input("请手动输入您想说的内容:")
        if manual_input:
            return manual_input
        return ""
        
    except Exception as e:
        st.error(f"麦克风访问错误: {e}")
        return ""

# Google语音识别，带重试机制
def try_google_recognition(recognizer, audio, max_retries=3):
    retry_count = 0
    while retry_count < max_retries:
        try:
            st.info(f"尝试使用Google语音识别 (尝试 {retry_count+1}/{max_retries})...")
            # 移除timeout参数，因为recognize_google不支持此参数
            text = recognizer.recognize_google(audio, language='zh-CN')
            st.success("Google语音识别成功")
            return text
        except sr.UnknownValueError:
            st.warning("未能识别语音内容")
            return ""
        except sr.RequestError as e:
            retry_count += 1
            error_msg = str(e)
            st.warning(f"Google语音识别请求失败 ({retry_count}/{max_retries}): {error_msg}")
            
            # 记录更详细的错误信息
            if "Bad Gateway" in error_msg:
                st.error("检测到Bad Gateway错误，可能是网络问题或Google服务在当前地区不可用")
            elif "Connection refused" in error_msg:
                st.error("连接被拒绝，请检查网络连接")
            elif "timed out" in error_msg:
                st.error("连接超时，请检查网络速度")
                
            if retry_count >= max_retries:
                st.error("Google语音识别服务不可用，尝试其他服务")
            import time
            time.sleep(2)  # 增加等待时间到2秒
    return ""

# Sphinx离线语音识别
def try_sphinx_recognition(recognizer, audio):
    try:
        st.info("尝试使用Sphinx离线识别...")
        # 不指定language参数，因为默认的英文模型可能比不完整的中文模型效果更好
        text = recognizer.recognize_sphinx(audio)
        
        if not text:
            st.warning("未能识别语音内容")
            return ""
            
        st.success("离线识别成功")
        st.info(f"识别结果: '{text}'")
        
        # 不再显示警告，直接返回结果
        return text
    except Exception as e:
        st.warning(f"Sphinx离线识别失败: {e}")
        return ""

# 尝试其他可用的识别服务
def try_other_recognition(recognizer, audio):
    # 可以添加其他语音识别服务，如百度、讯飞等
    # 这里仅作为示例
    try:
        st.info("尝试使用其他语音识别服务...")
        # 这里可以添加其他API的调用
        return ""
    except Exception as e:
        st.warning(f"其他语音识别服务失败: {e}")
        return ""

# 语音合成功能
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.say(text)
    engine.runAndWait()

# 语音输入按钮
if enable_voice:
    if st.button("🎤 语音输入"):
        speech_text = recognize_speech()
        if speech_text:
            # 直接处理识别结果，不需要额外确认
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "user",
                "content": speech_text,
                "timestamp": timestamp
            })
            with st.chat_message("user"):
                st.markdown(speech_text)
                st.caption(f"时间: {timestamp}")
            
            # 生成回答
            with st.spinner("思考中..."):
                if model_mode == "自动选择":
                    model = select_model(speech_text)
                else:
                    model = st.session_state.current_model
                
                response = generate_response(
                    speech_text,
                    model,
                    **st.session_state.model_params
                )
                
                # 添加情感回应
                if enable_emotion:
                    emotion_response = emotional_response(speech_text)
                    response = f"{emotion_response}\n{response}"
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": timestamp
                })
                with st.chat_message("assistant"):
                    st.markdown(response)
                    st.caption(f"时间: {timestamp}")
                
                # 语音播放回答
                text_to_speech(response)

# 文本输入处理
if prompt := st.chat_input("请输入您的问题"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(f"时间: {timestamp}")
    
    # 生成回答
    with st.spinner("思考中..."):
        if model_mode == "自动选择":
            model = select_model(prompt)
        else:
            model = st.session_state.current_model
        
        response = generate_response(
            prompt,
            model,
            **st.session_state.model_params
        )
        
        # 添加情感回应
        if enable_emotion:
            emotion_response = emotional_response(prompt)
            response = f"{emotion_response}\n{response}"
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
        with st.chat_message("assistant"):
            st.markdown(response)
            st.caption(f"时间: {timestamp}")
        
        # 如果启用了语音，播放回答
        if enable_voice:
            text_to_speech(response)
