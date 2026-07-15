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
    """尝试通过所有解密 API 获取解密后的原始字节内容"""
    encoded_url = urllib.parse.quote(encrypted_url, safe=':/?=&')
    for base in DECRYPT_URLS:
        full_url = base + encoded_url
        try:
            with urllib.request.urlopen(full_url, timeout=30) as resp:
                if resp.status == 200:
                    content_bytes = resp.read()
                    if content_bytes:
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

    # 写入文件
    with open(output_file, "wb") as f:
        f.write(content_bytes)

    file_size = len(content_bytes)
    print(f"✅ 已写入 {file_size} 字节到 {output_file}")

    # 预览内容（前200个字符），帮助调试
    preview = content_bytes[:200].decode('utf-8', errors='replace')
    print(f"📄 文件开头预览（UTF-8）:\n{preview}")

    # 如果文件为空（理论上不会，因为 content_bytes 非空），但以防万一
    if file_size == 0:
        print("❌ 写入的文件大小为 0，内容为空", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
