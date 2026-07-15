import sys
import os
import base64
import binascii
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ========== 工具函数 ==========

def ab2str(data: bytes) -> str:
    """字节转 UTF-8 字符串"""
    return data.decode('utf-8', errors='ignore')

def str2ab(text: str) -> bytes:
    """字符串转 UTF-8 字节"""
    return text.encode('utf-8')

def b64decode_bytes(b64_str: str) -> bytes:
    """Base64 解码"""
    return base64.b64decode(b64_str.strip())

# ========== 图片提取 ==========

def extract_config_from_image_data(data: bytes) -> bytes:
    """
    从图片二进制数据中提取配置（标记 '**' 之后的内容，Base64 解码）
    """
    marker = b'**'
    pos = data.find(marker)
    if pos == -1:
        raise ValueError("未找到标记 '**'，该图片可能不是由本工具生成。")
    encoded = data[pos + len(marker):]
    # 转为 ASCII 字符串（Base64）
    try:
        encoded_str = encoded.decode('ascii').strip()
    except UnicodeDecodeError:
        encoded_str = encoded.decode('utf-8', errors='ignore').strip()
    return base64.b64decode(encoded_str)

# ========== AES 解密 ==========

def decrypt_tvbox_text(content: str) -> str:
    """
    解密 TVBox 加密文本（十六进制格式）
    """
    data = content.strip()
    if not all(c in "0123456789abcdefABCDEF" for c in data):
        raise ValueError("输入不是有效的十六进制字符串")
    marker = "2324"
    idx = data.find(marker)
    if idx == -1:
        raise ValueError("未找到标记 #$，格式不正确")

    prefix_hex = data[:idx + len(marker)]
    cipher_hex = data[idx + len(marker):-26]
    iv_hex = data[-26:]

    if prefix_hex.startswith("2423"):
        key_hex = prefix_hex[4:-4]
    else:
        key_hex = prefix_hex[:-len(marker)]

    key_raw = bytes.fromhex(key_hex).decode('utf-8', errors='ignore')
    iv_raw = bytes.fromhex(iv_hex).decode('utf-8', errors='ignore')

    key_padded = key_raw.ljust(16, '0')
    iv_padded = iv_raw.ljust(16, '0')

    key_bytes = key_padded.encode('utf-8')
    iv_bytes = iv_padded.encode('utf-8')

    if len(key_bytes) < 16:
        key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
    if len(iv_bytes) < 16:
        iv_bytes = iv_bytes + b'\x00' * (16 - len(iv_bytes))

    cipher = AES.new(key_bytes[:16], AES.MODE_CBC, iv_bytes[:16])
    ciphertext = binascii.unhexlify(cipher_hex)
    plaintext_padded = cipher.decrypt(ciphertext)

    try:
        plaintext = unpad(plaintext_padded, AES.block_size).decode('utf-8', errors='ignore')
    except ValueError:
        plaintext = plaintext_padded.decode('utf-8', errors='ignore')
    return plaintext

# ========== 自动处理流程 ==========

def process_data(data: bytes) -> str:
    """
    自动识别并处理数据：
      - 如果是图片（含 '**'），提取配置。
      - 如果提取结果或原始数据是加密十六进制（含 '2324'），解密。
      - 否则直接返回文本（假定为 JSON）。
    """
    # 1. 检查是否为图片（含有 '**' 标记）
    if b'**' in data:
        try:
            extracted = extract_config_from_image_data(data)
            # 提取结果可能是二进制文本，尝试转为字符串
            text = ab2str(extracted)
            # 检查是否加密格式（十六进制且含 '2324'）
            text_clean = text.strip()
            if all(c in "0123456789abcdefABCDEF" for c in text_clean.replace(' ', '')) and '2324' in text_clean:
                print("🔐 检测到加密配置，正在解密...")
                return decrypt_tvbox_text(text_clean)
            else:
                print("✅ 提取到明文配置")
                return text
        except Exception as e:
            print(f"⚠️ 图片提取失败: {e}，尝试按普通文本处理...")
            # 降级处理

    # 2. 不是图片，或提取失败，尝试作为文本处理
    try:
        text = ab2str(data).strip()
        # 检查是否为加密格式
        if all(c in "0123456789abcdefABCDEF" for c in text.replace(' ', '')) and '2324' in text:
            print("🔐 检测到加密文本，正在解密...")
            return decrypt_tvbox_text(text)
        else:
            print("✅ 输入为明文配置")
            return text
    except Exception as e:
        raise ValueError(f"无法识别数据格式: {e}")

# ========== 网络下载 ==========

def download_url(url: str) -> bytes:
    """从 URL 下载数据，返回字节"""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content

# ========== 主入口 ==========

def main():
    if len(sys.argv) < 2:
        print("用法: python a.py <URL或本地文件路径> [输出文件名]")
        print("  例如: python a.py https://example.com/config.bmp my_config.json")
        sys.exit(1)

    source = sys.argv[1]
    out_name = sys.argv[2] if len(sys.argv) > 2 else "config.json"

    # 1. 获取数据
    if source.startswith(('http://', 'https://')):
        print(f"📥 正在从 URL 下载: {source}")
        try:
            data = download_url(source)
            print("✅ 下载成功")
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            sys.exit(1)
    else:
        # 本地文件
        print(f"📂 读取本地文件: {source}")
        try:
            with open(source, 'rb') as f:
                data = f.read()
            print("✅ 读取成功")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            sys.exit(1)

    # 2. 自动处理
    try:
        result_text = process_data(data)
        # 3. 保存结果
        with open(out_name, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"🎉 处理完成，结果已保存至: {out_name}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
