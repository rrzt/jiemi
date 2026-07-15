#!/usr/bin/env python3
"""
解密脚本：通过线上解密 API 获取解密后的内容，并原样写入指定文件。
用法: python jm.py <需解密的网址> <输出文件路径>
示例: python jm.py "https://example.com/encrypted.txt" config.json
"""

import sys
import urllib.request
import urllib.parse

# 解密 API 列表（按顺序尝试）
DECRYPT_URLS = [
    "https://feiyangdigital.v1.mk/api/jiemi.php?url=",
    "https://www.xn--sss604efuw.net/jm/jiemi.php?url=",
]


def decrypt_url(encrypted_url: str) -> bytes | None:
    """
    尝试通过所有解密 API 获取解密后的原始字节内容。
    返回 bytes 以便保留任何编码，写入时再按需解码。
    """
    # 对 URL 进行编码，保留结构字符
    encoded_url = urllib.parse.quote(encrypted_url, safe=':/?=&')
    for base in DECRYPT_URLS:
        full_url = base + encoded_url
        try:
            with urllib.request.urlopen(full_url, timeout=30) as resp:
                if resp.status == 200:
                    content_bytes = resp.read()
                    if content_bytes:  # 非空即认为成功
                        return content_bytes
                    else:
                        print(f"⚠️ API {base} 返回空内容，跳过", file=sys.stderr)
                else:
                    print(f"⚠️ API {base} 返回状态码 {resp.status}，跳过", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ 尝试 API {base} 失败: {e}", file=sys.stderr)
            continue
    return None


def main():
    if len(sys.argv) < 3:
        print("❌ 用法: python jm.py <需解密的网址> <输出文件路径>", file=sys.stderr)
        print("示例: python jm.py \"https://example.com/encrypted.txt\" config.json", file=sys.stderr)
        sys.exit(1)

    encrypted_url = sys.argv[1]
    output_file = sys.argv[2]

    print(f"⏳ 正在解密: {encrypted_url}")

    content_bytes = decrypt_url(encrypted_url)

    if content_bytes is None:
        print("❌ 所有解密 API 均失败，无法获取解密内容", file=sys.stderr)
        sys.exit(1)

    # 以二进制方式写入，避免编码问题；也可选择解码为字符串再写入，
    # 但二进制更安全，确保原样保留。
    with open(output_file, "wb") as f:
        f.write(content_bytes)

    # 打印文件大小供调试
    print(f"✅ 解密成功，已写入 {len(content_bytes)} 字节到 {output_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
