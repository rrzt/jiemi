import os
import json

# 定义输入和输出的文件名
INPUT_JSON = "tvbox_config.json"
OUTPUT_JSON = "tvbox_modified.json"  # 另存为新文件，不破坏原文件

# 你要注入的 jar 地址
JAR_KEY = "jar"
JAR_VALUE = "https://ghfast.top/https://raw.githubusercontent.com/woshishiq1/jiemi/main/aowu.png"

def add_jar_to_sites():
    # 1. 检查原始解密文件是否存在
    if not os.path.exists(INPUT_JSON):
        print(f"[-] 未找到源文件 {INPUT_JSON}，请确认上一步脚本是否成功运行。")
        return

    # 2. 读取原始 JSON 内容
    try:
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"[-] 读取或解析 {INPUT_JSON} 失败: {e}")
        return

    # 3. 检查并遍历 sites 字段
    sites_list = config_data.get("sites", [])
    if not sites_list or not isinstance(sites_list, list):
        print("[-] JSON 中未找到有效的 'sites' 列表，跳过处理。")
        return

    print(f"[+] 开始处理 'sites' 列表，共检测到 {len(sites_list)} 个站点...")

    # 4. 循环为每个站点对象注入 jar 字段
    for site in sites_list:
        if isinstance(site, dict):
            # 写入专属 jar 地址
            site[JAR_KEY] = JAR_VALUE

    # 5. 将修改后的数据独立写入全新的文件，格式完美对齐
    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            # indent=2 保证完美的层级缩进，ensure_ascii=False 保证中文正常显示
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"[+] 成功生成全新的外挂 Jar 配置文件: {OUTPUT_JSON}！")
    except Exception as e:
        print(f"[-] 保存新 JSON 文件失败: {e}")

if __name__ == "__main__":
    add_jar_to_sites()
