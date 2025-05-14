# Intelligent-Chat-Robot

<div align="center">
  <p><strong>基于大语言模型的多模态智能聊天助手</strong></p>
  <p>🏆 传智杯人工智能大模型创新应用挑战赛 国家一等奖 🏆</p>
</div>

## 📖 项目背景

智聊机器人是一个基于大语言模型的多模态智能聊天助手，专为传智杯人工智能大模型创新应用挑战赛开发。本项目旨在探索大语言模型在实际应用场景中的潜力，通过整合语音识别、情感分析和图像处理等技术，打造一个功能丰富、交互自然的智能助手系统。

项目立足于本地化部署和隐私保护，采用Ollama框架调用本地大语言模型，同时结合科大讯飞的语音识别技术，实现了一个既智能又保护用户隐私的聊天系统。在传智杯比赛中，该项目凭借其创新性、实用性和技术实现获得了国家一等奖的荣誉。

## ✨ 核心功能

- **智能对话**：基于本地部署的大语言模型（Qwen2、DeepSeek等）提供智能对话能力
- **多模态交互**：支持文本、语音和图像多种输入方式
- **情感识别**：能够分析用户情感并给予相应回应
- **语音交互**：集成科大讯飞和Google语音识别，支持语音输入和语音播报
- **图像分析**：支持上传图片并进行智能分析
- **自动模型选择**：根据用户输入内容智能选择最合适的AI模型
- **多语言支持**：支持中文、英文等多种语言的交互

## 🛠️ 技术架构

### 前端框架
- **Streamlit**：用于构建交互式Web界面

### 核心技术
- **大语言模型**：基于Ollama框架调用本地部署的Qwen2、DeepSeek-R1等模型
- **语音识别**：
  - 科大讯飞语音识别API
  - Google语音识别（备用）
  - Sphinx离线语音识别（备用）
- **语音合成**：基于pyttsx3的文本到语音转换
- **情感分析**：使用Hugging Face的transformers库进行情感识别
- **图像处理**：使用Pillow库处理上传的图像

### 系统架构
智聊机器人/
  - ├── app.py                # 主应用程序入口
  - ├── utils.py              # 工具函数和模型管理
  - ├── xunfei_speech.py      # 科大讯飞语音识别模块
  - ├── xunfei_config.py      # 科大讯飞API配置
  - ├── error_handler.py      # 错误处理模块
  - ├── response_processor.py # 响应处理模块
  - └── requirements.txt      # 项目依赖


## 🚀 安装与使用

### 环境要求

- Python 3.8+
- Ollama服务（用于本地部署大语言模型）
- 科大讯飞开发者账号（用于语音识别）

### 安装步骤

1. 克隆项目到本地

```bash
git clone https://github.com/your-username/zhichat-bot.git
cd zhichat-bot
```

2. 安装依赖包
```bash
pip install -r requirements.txt
```

3. 安装并启动Ollama服务
```bash
# 安装Ollama（根据操作系统选择合适的安装方法）
# 启动Ollama服务
ollama serve
```

拉取所需模型
ollama pull qwen2
ollama pull deepseek-r1

4. 配置科大讯飞API
编辑 xunfei_config.py 文件，填入您的科大讯飞API密钥：
APPID = '您的APPID'
API_KEY = '您的API_KEY'
API_SECRET = '您的API_SECRET'

### 运行应用
```bash
streamlit run app.py
```
应用将在浏览器中自动打开，默认地址为： http://localhost:8501

## 💡 使用技巧
- 模型选择 ：可以在侧边栏选择自动或手动模式来控制使用的AI模型
- 语音交互 ：点击"语音输入"按钮开始语音识别
- 图片分析 ：通过上传图片功能可以让AI分析图像内容
- 参数调整 ：在侧边栏可以调整模型的温度和采样阈值等参数
- 多语言支持 ：可以在侧边栏切换界面语言

## 🏆 获奖情况
本项目在传智杯人工智能大模型创新应用挑战赛中荣获 国家一等奖 ，评委对项目的创新性、技术实现和实用价值给予了高度评价。

## 📝 许可证
MIT License

## 👥 贡献者
- 许语梦
## 📞 联系方式
如有任何问题或建议，请通过以下方式联系我们：

- 邮箱： 2332257041@qq.com
- GitHub Issues： 提交问题
