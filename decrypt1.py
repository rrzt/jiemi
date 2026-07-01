import base64
import json
import re
import requests

def decrypt_tvbox_config(webp_url):
    """增强版：支持重定向 + 伪装页面"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    print(f"正在访问: {webp_url}")
    try:
        session = requests.Session()
        res = session.get(webp_url, headers=headers, timeout=15, allow_redirects=True)
        print(f"最终状态码: {res.status_code}，最终URL: {res.url}")
        
        if res.status_code != 200:
            print(f"❌ 下载失败: {res.status_code}")
            return None
            
        content = res.text.strip()
        print(f"内容长度: {len(content)} 字符")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

    # 1. 尝试直接JSON
    try:
        return json.loads(content)
    except:
        pass

    # 2. 增强Base64提取（处理伪装页面）
    try:
        # 提取所有可能的Base64块
        base64_pattern = re.compile(r'[A-Za-z0-9+/=]{100,}')  # 至少100字符
        blocks = base64_pattern.findall(content)
        
        for block in sorted(blocks, key=len, reverse=True):  # 从最长的开始尝试
            try:
                # 补全padding
                padding = len(block) % 4
                if padding:
                    block += "=" * (4 - padding)
                
                decoded_bytes = base64.b64decode(block, validate=False)
                decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
                
                # 提取JSON
                json_match = re.search(r'\{.*\}', decoded_str, re.DOTALL)
                if json_match:
                    config = json.loads(json_match.group(0))
                    print("🎉 Base64解密成功！")
                    return config
            except:
                continue
    except Exception as e:
        print(f"Base64尝试失败: {e}")

    # 3. 调用2015888解密接口（你原来脚本里的）
    print("尝试调用在线解密接口...")
    try:
        api_res = requests.post(
            "https://master.2015888.xyz/jiemi/",
            data={"url": webp_url, "content": content[:50000]},  # 避免太长
            headers=headers,
            timeout=20
        )
        match = re.search(r'<textarea[^>]*>(.*?)</textarea>', api_res.text, re.S | re.I)
        if match:
            text = match.group(1).strip()
            return json.loads(text)
    except Exception as e:
        print(f"在线接口失败: {e}")

    print("❌ 所有方法都失败")
    return None

if __name__ == "__main__":
    target_url = "http://我不是.摸鱼儿.top"   # 或加上 /config.webp 等路径
    config_data = decrypt_tvbox_config(target_url)
    
    if config_data:
        output_file = "tvbox_config1.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功保存到: {output_file}")
        print(f"站点数量: {len(config_data.get('sites', []))}")
    else:
        print("❌ 解密失败")
