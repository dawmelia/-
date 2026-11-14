import requests
import json
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
API = "https://wiki.biligame.com/sgs/api.php"
CACHE_BREAKPOINT = "breakpoint.json"
OUTPUT_PATH = "static/sgs_data.json"

def get_first_value(lst):
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

def save_breakpoint(offset, data_list):
    """保存断点：当前offset + 已经拿到的全部数据"""
    with open(CACHE_BREAKPOINT, "w", encoding="utf-8") as f:
        json.dump({
            "last_offset": offset,
            "data": data_list
        }, f, ensure_ascii=False, indent=2)

def load_breakpoint():
    """读取断点，没有断点就返回offset=0，空列表"""
    if not os.path.exists(CACHE_BREAKPOINT):
        return 0, []
    try:
        with open(CACHE_BREAKPOINT, "r", encoding="utf-8") as f:
            bp = json.load(f)
        return bp.get("last_offset", 0), bp.get("data", [])
    except Exception:
        return 0, []

def main():
    # 加载上次断点
    offset, all_data = load_breakpoint()
    print(f"📌 读取断点，上次offset={offset}，已有 {len(all_data)} 条数据")

    while True:
        ret = smw_ask_query(offset)
        if ret is None:
            print("❗ 当前offset拉取失败，暂停，下次启动继续从这个offset跑")
            save_breakpoint(offset, all_data)
            return
        results = ret.get("query", {}).get("results", {})
        if not results:
            print("✅ 没有更多数据了，分页读取完毕")
            break

        for skill_name, info in results.items():
            printouts = info.get("printouts", {})
            skill = skill_name.replace("技能:", "")
            hero = get_first_value(printouts.get("所属武将", []))
            skill_type = get_first_value(printouts.get("技能类型", []))
            skill = skill.strip()
            hero = hero.strip()
            skill_type = skill_type.strip()
            all_data.append({
                "技能": skill,
                "所属武将": hero,
                "技能类型": skill_type
            })

        offset += 500
        print(f"✅ 已拉取，累计 {len(all_data)} 条，下一次offset={offset}")
        # 每跑完一页就保存断点，防止断连丢失
        save_breakpoint(offset, all_data)
        time.sleep(1)

    # 全部拉完之后统一去重
    seen_keys = set()
    clean_data = []
    for item in all_data:
        key = (item["技能"], item["所属武将"])
        if key not in seen_keys:
            seen_keys.add(key)
            clean_data.append(item)
    print(f"\n去重前：{len(all_data)} 条，去重后：{len(clean_data)} 条")

    os.makedirs("static", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 最终结果保存到 {OUTPUT_PATH}，一共 {len(clean_data)} 条")

    # 全部跑完之后，可以选择清空断点（注释掉就保留断点）
    # os.remove(CACHE_BREAKPOINT)

if __name__ == "__main__":
    main()
