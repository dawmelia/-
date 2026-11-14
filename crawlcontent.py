import requests
import json
import time
import re
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
API = "https://wiki.biligame.com/sgs/api.php"
SLEEP = 1.5
CACHE_FILE = "skill_content_cache.json"
INPUT = "static/sgs_data.json"
OUTPUT = "static/sgs_full.json"

def fetch_desc(skill_name):
    params = {
        "action": "parse",
        "page": skill_name,
        "prop": "wikitext",
        "format": "json"
    }
    try:
        resp = requests.get(API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        wikitext = resp.json()["parse"]["wikitext"]["*"]
        m1 = re.search(r"\|经典技能描述=(.*?)(?=\|\w+=|\n\}\})", wikitext, re.S)
        if m1:
            return m1.group(1).strip()
        m2 = re.search(r"\|界限技能描述=(.*?)(?=\|\w+=|\n\}\})", wikitext, re.S)
        if m2:
            return m2.group(1).strip()
        m3 = re.search(r"\|描述=(.*?)(?=\|\w+=|\n\}\})", wikitext, re.S)
        if m3:
            return m3.group(1).strip()
        return ""
    except Exception as e:
        print(f"❌ {skill_name} 失败：{e}")
        return None

def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        skill_list = json.load(f)

    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

    for item in skill_list:
        s = item["技能"]
        h = item["所属武将"]
        key = f"{s}||{h}"
        if key in cache:
            print(f"✅ 跳过缓存：{s}")
            continue
        print(f"🔄 抓取：{s}")
        desc = fetch_desc(s)
        if desc is not None:
            item["技能内容"] = desc
            cache[key] = item
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        time.sleep(SLEEP)

    final = list(cache.values())
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 完成，输出 {OUTPUT}，共 {len(final)} 条")

if __name__ == "__main__":
    main()
