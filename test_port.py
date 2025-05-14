import socket

def check_port_available(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        print(f"{port}端口可用")
        s.close()
        return True
    except socket.error as e:
        print(f"{port}端口已被占用: {e}")
        return False
    finally:
        s.close()

def find_available_port(start_port=8501, max_attempts=10):
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    return None

if __name__ == '__main__':
    port = find_available_port()
    if port:
        print(f"找到可用端口: {port}")
    else:
        print(f"未找到可用端口")