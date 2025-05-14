import ollama
from langdetect import detect
import re
import emoji
from transformers import pipeline
import logging
from typing import Dict, Optional, Any

class OllamaModelManager:
    def __init__(self):
        self.client = ollama.Client()
        self.models = {
            'qwen2': {
                'name': 'qwen2',
                'temperature': 0.7,
                'top_p': 0.9,
                'context_length': 2048
            },
            'deepseek-r1': {
                'name': 'deepseek-r1',
                'temperature': 0.8,
                'top_p': 0.9,
                'context_length': 4096
            }
        }
        self.default_model = 'qwen2'
        self._initialize_models()

    def _check_ollama_service(self):
        import socket
        try:
            # 检查Ollama默认端口(11434)是否可访问
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 11434))
            sock.close()
            print(f"Ollama服务端口检查结果: {result == 0}")
            return result == 0
        except Exception as e:
            print(f"检查Ollama服务时出错: {e}")
            return False

    def _initialize_models(self):
        try:
            # print("正在检查Ollama服务...")
            # 获取可用模型列表
            available_models = self.client.list()
            # print(f"Ollama返回数据: {available_models}")
            
            # 适配新的API返回类型
            model_names = []
            if hasattr(available_models, 'models'):
                # 新版API返回ListResponse对象
                model_names = [model.model.split(':')[0] for model in available_models.models]
            
            # print(f"已安装的模型: {model_names}")
            
            # 检查所需模型是否都已安装，允许模型名称前缀匹配
            missing_models = []
            for model in self.models.keys():
                # 检查是否有匹配的模型名称（允许前缀匹配，如deepseek-r1匹配deepseek）
                if not any(installed.startswith(model) or model.startswith(installed) for installed in model_names):
                    missing_models.append(model)
            
            # 更新模型名称为实际安装的名称
            for model_key in list(self.models.keys()):
                for installed in model_names:
                    if installed.startswith(model_key) and installed != model_key:
                        # 找到匹配的模型，更新配置
                        print(f"将使用 {installed} 替代 {model_key}")
                        config = self.models[model_key].copy()
                        config['name'] = installed
                        self.models[model_key] = config
            
            if missing_models:
                print("\n需要安装以下模型:")
                for model in missing_models:
                    print(f"- {model}: 请执行命令 'ollama pull {model}'")
                print("\n请安装完所需模型后重新启动应用。\n")
                return False
            
            # print("✓ Ollama服务连接成功")
            # print("✓ 所需模型已全部安装\n")
            return True
        except Exception as e:
            print(f"❌ 连接Ollama服务失败: {e}")
            print("请确保Ollama服务已启动，并且已安装所需模型")
            return False

    def generate_response(self, prompt: str, model_name: str, **kwargs) -> str:
        from error_handler import ErrorHandler, RetryStrategy
        
        @ErrorHandler.with_retry(RetryStrategy(max_retries=3, delay=1.0, backoff=2.0))
        def _generate(self, prompt: str, model_name: str) -> str:
            model_config = self.models.get(model_name, self.models[self.default_model])
            result = self.client.generate(model_name, prompt)
            return result['response']
        
        return _generate(self, prompt, model_name)

class LanguageProcessor:
    @staticmethod
    def detect_language(text: str) -> str:
        try:
            return detect(text)
        except:
            return 'en'

    @staticmethod
    def select_model(prompt: str) -> str:
        if re.search(r'\b(专业|技术|学术|代码|编程)\b', prompt):
            return 'deepseek'
        return 'qwen2'

class EmotionAnalyzer:
    def __init__(self):
        self.analyzer = self._initialize_analyzer()
        self.responses = {
            'joy': "太棒啦🎉 希望您一直保持这份好心情！",
            'sadness': "别难过😢 我会一直陪着您的。",
            'anger': "消消气🥺 有什么问题我们慢慢解决。",
            'fear': "别怕别怕🙌 我会保护您的。",
            'neutral': "了解啦，请您继续说。"
        }

    def _initialize_analyzer(self):
        try:
            from transformers import logging as transformers_logging
            transformers_logging.set_verbosity_error()
            return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
        except Exception as e:
            logging.warning(f"无法加载情感分析模型: {e}")
            return None

    def analyze(self, text: str) -> str:
        if not self.analyzer:
            return self._keyword_based_analysis(text)
        
        try:
            result = self.analyzer(text)[0]
            return self.responses.get(result['label'], self.responses['neutral'])
        except Exception as e:
            logging.error(f"情感分析出错: {e}")
            return self.responses['neutral']

    def _keyword_based_analysis(self, text: str) -> str:
        text = text.lower()
        if any(word in text for word in ['开心', '高兴', '棒']):
            return self.responses['joy']
        elif any(word in text for word in ['难过', '伤心', '哭']):
            return self.responses['sadness']
        elif any(word in text for word in ['生气', '愤怒', '气死']):
            return self.responses['anger']
        elif any(word in text for word in ['害怕', '恐惧', '吓']):
            return self.responses['fear']
        return self.responses['neutral']

# 初始化全局实例
model_manager = OllamaModelManager()
language_processor = LanguageProcessor()
emotion_analyzer = EmotionAnalyzer()

# 修改导出函数
def generate_response(prompt: str, model: str, **kwargs) -> str:
    # 获取原始响应
    response = model_manager.generate_response(prompt, model, **kwargs)
    
    # 导入并使用响应处理器清理输出
    from response_processor import clean_response
    return clean_response(response)

def select_model(prompt: str) -> str:
    return language_processor.select_model(prompt)

def detect_language(text: str) -> str:
    return language_processor.detect_language(text)

def emotional_response(prompt: str) -> str:
    return emotion_analyzer.analyze(prompt)