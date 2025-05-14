import websocket
import datetime
import hashlib
import base64
import hmac
import json
import time
import ssl
import threading
from urllib.parse import urlencode
import requests
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
from xunfei_config import *

APPID = "259650ba"

class XunfeiASR:
    def __init__(self):
        self.result = ""
        self.ws = None
        self.is_listening = False
        self.retry_count = 0
        self.max_retries = 3  # 减少最大重试次数
        self.retry_delay = 5.0  # 增加初始重试延迟
        self.last_request_time = 0  # 记录上次请求时间
        self.min_request_interval = 10.0  # 最小请求间隔时间（秒）

    def exponential_backoff(self):
        """指数退避算法计算下一次重试的延迟时间"""
        delay = min(30, self.retry_delay * (2 ** self.retry_count))  # 最大延迟30秒
        time.sleep(delay)
        self.retry_count += 1
        return self.retry_count < self.max_retries

    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = f'host: rtasr.xfyun.cn\ndate: {date}\nGET /v1/ws HTTP/1.1'
        
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(API_SECRET.encode('utf-8'),
                                signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        params = {'authorization': authorization, 'date': date, 'host': 'rtasr.xfyun.cn'}
        return f'{ASR_URL}?{urlencode(params)}'

    def on_message(self, ws, message):
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                print(f"错误码：{code}，错误详情：{ERROR_CODES.get(str(code), '未知错误')}")
                ws.close()
                return
            
            data = json.loads(message)["data"]
            text = json.loads(data)["result"]
            if text:
                self.result += text
        except Exception as e:
            print(f"处理消息时发生错误：{e}")

    def on_error(self, ws, error):
        print(f"### error: {error}")

    def on_close(self, ws, *args):
        print("### closed ###")
        self.is_listening = False

    def on_open(self, ws):
        def run(*args):
            try:
                if not self.is_listening:
                    return
                data = {"common": {"app_id": APPID},
                       "business": {"language": DEFAULT_LANGUAGE, "accent": DEFAULT_ACCENT},
                       "data": {"status": 2, "format": DEFAULT_FORMAT,
                               "encoding": "raw"}}
                ws.send(json.dumps(data))
            except Exception as e:
                print(f"发送初始化数据时发生错误：{e}")
                self.is_listening = False
                ws.close()
        thread.start_new_thread(run, ())

    def start_listening(self):
        self.result = ""
        self.retry_count = 0
        self.is_listening = True
        base_delay = 10.0  # 增加基础延迟到10秒
        max_consecutive_errors = 2  # 减少连续错误次数限制
        consecutive_errors = 0  # 当前连续错误次数
        
        while True:
            try:
                if not self.is_listening:
                    break
                    
                # 检查距离上次请求的时间间隔
                current_time = time.time()
                time_since_last_request = current_time - self.last_request_time
                min_interval = max(self.min_request_interval, base_delay * (1 + self.retry_count))  # 更激进的动态增加请求间隔
                if time_since_last_request < min_interval:
                    wait_time = min_interval - time_since_last_request
                    print(f"等待{wait_time:.1f}秒以遵守访问频率限制...")
                    time.sleep(wait_time)
                
                # 重置WebSocket连接
                if self.ws:
                    try:
                        self.ws.close()
                    except:
                        pass
                    self.ws = None
                
                websocket.enableTrace(False)
                wsUrl = self.create_url()
                self.ws = websocket.WebSocketApp(wsUrl,
                                           on_message=self.on_message,
                                           on_error=self.on_error,
                                           on_close=self.on_close,
                                           on_open=self.on_open)
                self.is_listening = True
                self.last_request_time = time.time()  # 更新请求时间
                
                # 设置连接超时
                self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=30, ping_timeout=10)
                
                # 如果连接正常关闭，跳出循环
                if not self.is_listening:
                    break
                
                # 重置连续错误计数
                consecutive_errors = 0
                
                # 如果遇到错误，尝试重试
                if self.exponential_backoff():
                    print(f"正在进行第{self.retry_count}次重试...等待{min_interval}秒")
                    continue
                else:
                    print("达到最大重试次数，停止重试")
                    break
                    
            except Exception as e:
                print(f"连接发生错误: {e}")
                consecutive_errors += 1
                
                # 如果连续错误次数过多，终止重试
                if consecutive_errors >= max_consecutive_errors:
                    print("连续错误次数过多，终止重试")
                    break
                    
                if not self.exponential_backoff():
                    break
                time.sleep(min_interval)  # 发生错误时也需要等待

    def stop_listening(self):
        if self.ws:
            self.ws.close()
        self.is_listening = False
        return self.result

def recognize_with_xunfei(audio_data):
    """使用讯飞语音识别处理音频数据"""
    try:
        asr = XunfeiASR()
        asr.start_listening()
        
        # 处理音频数据
        if isinstance(audio_data, bytes):
            # 如果是原始音频数据，直接使用
            audio_bytes = audio_data
        else:
            # 如果不是bytes类型，尝试转换
            audio_bytes = bytes(audio_data)
        
        # 发送音频数据进行识别
        try:
            if asr.ws and asr.is_listening:
                asr.ws.send(audio_bytes, websocket.ABNF.OPCODE_BINARY)
                time.sleep(1)  # 等待处理完成
                
                # 获取识别结果
                result = asr.stop_listening()
                if result:
                    return result.strip()
        except (websocket.WebSocketException, BrokenPipeError) as e:
            print(f"发送音频数据时发生错误：{e}")
        finally:
            if asr.ws:
                asr.stop_listening()
        return None
    except Exception as e:
        print(f"讯飞语音识别出错: {e}")
        return None

class XunfeiTTS:
    def __init__(self):
        self.URL = TTS_URL

    def create_header(self):
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = f'host: tts-api.xfyun.cn\ndate: {date}\nGET /v2/tts HTTP/1.1'
        
        # hmac-sha256加密
        signature_sha = hmac.new(API_SECRET.encode('utf-8'),
                                signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        return {
            'Content-Type': 'application/json',
            'Authorization': authorization,
            'Date': date,
            'Host': 'tts-api.xfyun.cn'
        }

    def text_to_speech(self, text, output_file='output.wav'):
        try:
            data = {
                'common': {'app_id': APPID},
                'business': {
                    'aue': 'raw',
                    'auf': 'audio/L16;rate=16000',
                    'vcn': 'xiaoyan',
                    'tte': 'utf8'
                },
                'data': {
                    'text': base64.b64encode(text.encode('utf8')).decode('utf8'),
                    'status': 2
                }
            }

            response = requests.post(self.URL, json=data, headers=self.create_header())
            if response.status_code == 200:
                result = response.json()
                if result['code'] == 0:
                    audio_data = base64.b64decode(result['data']['audio'])
                    with open(output_file, 'wb') as f:
                        f.write(audio_data)
                    return True, None
                else:
                    return False, f"合成失败，错误码：{result['code']}"
            else:
                return False, f"请求失败，状态码：{response.status_code}"
        except Exception as e:
            return False, f"语音合成出错: {e}"