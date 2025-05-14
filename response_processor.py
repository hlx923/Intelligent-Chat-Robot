import re

def clean_response(response: str) -> str:
    """清理模型输出中的XML标签和其他不需要的内容
    
    Args:
        response: 原始响应文本
        
    Returns:
        清理后的响应文本
    """
    # 移除<think>标签及其内容
    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
    
    # 移除其他可能的XML标签
    response = re.sub(r'<[^>]+>', '', response)
    
    # 移除多余的空行
    response = '\n'.join(line for line in response.splitlines() if line.strip())
    
    # 移除开头和结尾的空白字符
    response = response.strip()
    
    return response