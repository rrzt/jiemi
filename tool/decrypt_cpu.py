import base64
import json
import re
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
    # 绝大多数 TVBox 工具的前端解密核心就是将数据剔除乱码后进行 Base64 解码
    try:
        # 移除可能存在的伪装图片头等杂质，只保留合法 Base64 字符
        base64_pattern = re.compile(r"[A-Za-z0-9+/=]+")
        blocks = base64_pattern.findall(content)
        if blocks:
            # 拼接最长的一段，或者尝试全拼接
            longest_block = max(blocks, key=len)
            # 补齐 Base64 填充
            missing_padding = len(longest_block) % 4
            if missing_padding:
                longest_block += "=" * (4 - missing_padding)

            decoded_bytes = base64.b64decode(longest_block)
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")

            # 提取其中完整的 {} JSON 结构
            json_match = re.search(r"\{.*\}", decoded_str, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
    except Exception as e:
        print(f"⚠️ 自定义 Base64 解密尝试失败: {e}，将尝试调用解密网站接口...")

    # 3. 如果本地算法没解开，直接调用 2015888.xyz 网站背后的通用 API 接口
    # 模拟请求它的后台解密引擎
    api_url = "https://master.2015888.xyz/api/jiemi"  # 对应 /jiemi/ 页面的公共后台
    # 如果抓包发现是直接请求另一个接口，也可以替换它
    payload = {"url": webp_url, "content": content}

    try:
        api_res = requests.post(
            "https://master.2015888.xyz/jiemi/", data=payload, headers=headers
        )
        # 如果网站是用传统的 Form 表单或者特定的参数，可以通过正则匹配它返回的 textarea 内容
        match = re.search(r"<textarea[^>]*>(.*?)</textarea>", api_res.text, re.S)
        if match:
            return json.loads(match.group(1).strip())
    except:
        pass

    # 4. 后备兜底：由于你在上一步截图里已经能完美显示了，说明目前该网站纯支持外部调用
    # 如果遇到特殊魔改的 AES 加密，我们可以通过传入内容让它返回
    print("❌ 无法自动还原，请检查该加密源是否更新了高强度的自定义Key。")
    return None


if __name__ == "__main__":
    # 按需修改，你的目标 webp 订阅源 
    target_url = "https://raw.githubusercontent.com/IY-CPU/IY/main/%E5%A4%A9%E7%A5%9EIY.png"
    #target_url = "http://itv666.cc/aowu/config.webp"
    #https://raw.githubusercontent.com/IY-CPU/IY/main/%E5%A4%A9%E7%A5%9EIY.png
    #https://raw.githubusercontent.com/rrzt/jiemi/main/mw.json

    config_data = decrypt_tvbox_config(target_url)

    if config_data:
        # 规范化保存为本地 JSON 文件，按需修改output_file
        output_file = "cpu_config.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f"🎉 成功！解密后的影视源已保存到本地: {output_file}")
    else:
        print("❌ 解密失败。")
