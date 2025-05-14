import time
from functools import wraps
import logging
from typing import Callable, Any, Optional

class RetryStrategy:
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff

class ErrorHandler:
    @staticmethod
    def with_retry(strategy: Optional[RetryStrategy] = None) -> Callable:
        if not strategy:
            strategy = RetryStrategy()

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                delay = strategy.delay

                for attempt in range(strategy.max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < strategy.max_retries - 1:
                            logging.warning(f"尝试 {attempt + 1}/{strategy.max_retries} 失败: {str(e)}")
                            time.sleep(delay)
                            delay *= strategy.backoff
                        else:
                            logging.error(f"所有重试都失败了: {str(e)}")
                            break

                # 如果所有重试都失败了，返回友好的错误信息
                error_msg = str(last_exception)
                if '502' in error_msg:
                    return "抱歉，服务器暂时无法响应，请稍后再试。"
                return f"抱歉，发生了错误: {error_msg}"

            return wrapper
        return decorator