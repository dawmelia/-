import requests
import json
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
API = "https://wiki.biligame.com/sgs/api.php"

def get_first_value(lst):
    # 安全取列表第一个元素，空列表返回空字符串
    if isinstance(lst, list) and len(lst) > 0:
        return lst[0]
    return ""

def smw_ask_query(offset=0, retry=2):
    params = {
        "action": "ask",
        "query": "[[分类:技能]]|?所属武将|?技能类型",
        "limit": 500,
        "offset": offset,
        "format": "json"
    }
    for i in range(retry + 1):
        resp = requests.get(API, params=params, headers=HEADERS, timeout=30)
        try:
            return resp.json()
        except json.JSONDecodeError:
            if i < retry:
                print(f"⚠️ offset={offset} 被拦截，第{i+1}次重试，等待5s...")
                time.sleep(5)
            else:
                print(f"❌ offset={offset} 重试全部失败，响应文本：{resp.text[:200]}")
                return None

def main():
    all_data = []
    offset = 0
    while True:
        ret = smw_ask_query(offset)
        if ret is None:
            break
        results = ret.get("query", {}).get("results", {})
        if not results:
            break
        for skill_name, info in results.items():
            printouts = info.get("printouts", {})
            skill = skill_name.replace("技能:", "")
            hero = get_first_value(printouts.get("所属武将", []))
            skill_type = get_first_value(printouts.get("技能类型", []))
            # 清洗首尾空格
            skill = skill.strip()
            hero = hero.strip()
            skill_type = skill_type.strip()
            all_data.append({
                "技能": skill,
                "所属武将": hero,
                "技能类型": skill_type
            })
        offset += 500
        print(f"已拉取 {len(all_data)} 条")
        time.sleep(1)

    # ========== 去重逻辑：(技能,所属武将)相同才算重复，同名不同武将保留 ==========
    seen_keys = set()
    clean_data = []
    for item in all_data:
        key = (item["技能"], item["所属武将"])
        if key not in seen_keys:
            seen_keys.add(key)
            clean_data.append(item)
    print(f"\n去重前：{len(all_data)} 条，去重后：{len(clean_data)} 条")
    # =========================================================================

    os.makedirs("static", exist_ok=True)
    with open("static/sgs_data.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 全部完成，一共 {len(clean_data)} 条")

if __name__ == "__main__":
    main()
