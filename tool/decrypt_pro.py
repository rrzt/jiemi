import base64
import json
import re
import sys
import requests


def decrypt_tvbox_config(webp_url):
    """抓取 webp 加密文件并尝试自动解密"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"正在从目标地址下载加密文件: {webp_url}...")
    try:
        res = requests.get(webp_url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"❌ 下载文件失败，状态码: {res.status_code}")
            return None
        content = res.text.strip()
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

    print("文件下载成功，正在尝试解密...")

    # 1. 尝试直接作为 JSON 解析（防止根本没加密，只是换了后缀）
    try:
        return json.loads(content)
    except:
        pass

    # 2. 如果是 Base64 变体加密，或者包含特殊字符，先进行清洗
    try:
        base64_pattern = re.compile(r"[A-Za-z0-9+/=]+")
        blocks = base64_pattern.findall(content)
        if blocks:
            longest_block = max(blocks, key=len)
            missing_padding = len(longest_block) % 4
            if missing_padding:
                longest_block += "=" * (4 - missing_padding)

            decoded_bytes = base64.b64decode(longest_block)
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")

            json_match = re.search(r"\{.*\}", decoded_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
    except Exception as e:
        print(f"⚠️ 自定义 Base64 解密尝试失败: {e}，将尝试调用解密网站接口...")

    # 3. 如果本地算法没解开，直接调用 2015888.xyz 网站背后的通用 API 接口
    api_url = "https://master.2015888.xyz/api/jiemi"  # 对应 /jiemi/ 页面的公共后台
    payload = {"url": webp_url, "content": content}

    try:
        api_res = requests.post(
            "https://master.2015888.xyz/jiemi/", data=payload, headers=headers
        )
        match = re.search(r"<textarea[^>]*>(.*?)</textarea>", api_res.text, re.S)
        if match:
            return json.loads(match.group(1).strip())
    except:
        pass

    print("❌ 无法自动还原，请检查该加密源是否更新了高强度的自定义Key。")
    return None


if __name__ == "__main__":
    # 解析命令行参数
    if len(sys.argv) < 2:
        print("用法: python jiem.py <加密文件URL> [输出JSON文件名]")
        print("示例: python jiem.py https://example.com/config.webp output.json")
        sys.exit(1)

    target_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "config.json"

    config_data = decrypt_tvbox_config(target_url)

    if config_data:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f"🎉 成功！解密后的影视源已保存到本地: {output_file}")
    else:
        print("❌ 解密失败。")
        sys.exit(1)
