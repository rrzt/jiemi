#!/usr/bin/env python3
"""
解密脚本：通过线上解密 API 解密给定的加密网址，将结果保存到指定的输出文件。
用法: python jm.py <需解密的网址> <输出文件路径>
示例: python jm.py "https://example.com/encrypted.txt" config.json
"""

import sys
import urllib.request
import urllib.parse

# 解密 API 列表（按顺序尝试）
DECRYPT_URLS = [
    "https://feiyangdigital.v1.mk/api/jiemi.php?url=",
    "https://www.饭太硬.net/jm/jiemi.php?url=",
]


def decrypt_url(encrypted_url: str) -> str | None:
    """尝试通过所有解密 API 获取解密后的内容，成功则返回内容字符串，否则返回 None"""
    encoded_url = urllib.parse.quote(encrypted_url, safe='')
    for base in DECRYPT_URLS:
        full_url = base + encoded_url
        try:
            with urllib.request.urlopen(full_url, timeout=30) as resp:
                if resp.status == 200:
                    content = resp.read().decode('utf-8')
                    if content.strip():
                        return content
        except Exception:
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

    decrypted_content = decrypt_url(encrypted_url)

    if decrypted_content is None:
        print("❌ 所有解密 API 均失败，无法获取解密内容", file=sys.stderr)
        sys.exit(1)

    # 写入指定的输出文件（覆盖）
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(decrypted_content)

    print(f"✅ 解密成功，内容已保存至 {output_file}")
    sys.exit(0)


if __name__ == "__main__":
    main()
