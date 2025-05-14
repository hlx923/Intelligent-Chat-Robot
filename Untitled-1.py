def _initialize_models(self):
    try:
        print("正在检查Ollama服务...")
        # 简单测试连接
        response = self.client.embeddings(model="qwen2", prompt="test")
        print("✓ Ollama服务连接成功")
        return True
    except Exception as e:
        print(f"❌ 连接Ollama服务失败: {e}")
        print("请确保Ollama服务已启动，并且已安装所需模型")
        return False