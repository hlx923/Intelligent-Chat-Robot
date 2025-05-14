# 科大讯飞语音识别配置
# 请将以下配置替换为您在科大讯飞开放平台申请的实际值
APPID = '259650ba'
API_KEY = 'b2c0c0b2c0c0b2c0c0b2c0c0b2c0c0b2'
API_SECRET = 'ad249893de41cd1fb78df11d4962a272'

# 语音识别配置
ASR_URL = 'wss://rtasr.xfyun.cn/v1/ws'

# 语音合成配置
TTS_URL = 'https://tts-api.xfyun.cn/v2/tts'

# 默认参数配置
DEFAULT_FORMAT = 'wav'
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_LANGUAGE = 'zh_cn'
DEFAULT_ACCENT = 'mandarin'

# 错误码映射
ERROR_CODES = {
    '10105': '没有权限',
    '10106': '访问频率受限',
    '10107': '引擎服务器繁忙',
    '10109': '语音识别失败',
    '10110': '未检测到语音',
    '10111': '语音数据过长',
    '10112': '语音数据为空',
}