import requests
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
API = "https://wiki.biligame.com/sgs/api.php"

def get_first_value(lst):
    # 安全取列表第一个元素，空列表返回空字符串
    if isinstance(lst, list) and len(lst) > 0:
        return lst[0]
    return ""

def smw_ask_query(offset=0):
    params = {
        "action": "ask",
        "query": "[[分类:技能]]|?所属武将|?技能类型|limit=500|offset="+str(offset),
        "format": "json"
    }
    resp = requests.get(API, params=params, headers=HEADERS, timeout=30)
    return resp.json()

def main():
    all_data = []
    offset = 0
    while True:
        ret = smw_ask_query(offset)
        results = ret.get("query", {}).get("results", {})
        if not results:
            break
        for skill_name, info in results.items():
            printouts = info.get("printouts", {})
            skill = skill_name.replace("技能:", "")
            hero = get_first_value(printouts.get("所属武将", []))
            skill_type = get_first_value(printouts.get("技能类型", []))
            all_data.append({
                "技能": skill,
                "所属武将": hero,
                "技能类型": skill_type
            })
        offset += 500
        print(f"已拉取 {len(all_data)} 条")

    # 直接输出到安卓assets目录，重点改动这里
    out_path = "static/sgs_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 全部完成，一共 {len(all_data)} 条，文件写入：{out_path}")

if __name__ == "__main__":
    main()
