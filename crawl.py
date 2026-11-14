import requests
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
API = "https://wiki.biligame.com/sgs/api.php"

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
            all_data.append({
                "技能": skill_name.replace("技能:", ""),
                "所属武将": info.get("printouts", {}).get("所属武将", [None])[0],
                "技能类型": info.get("printouts", {}).get("技能类型", [None])[0]
            })
        offset += 500
        print(f"已拉取 {len(all_data)} 条")

    os.makedirs("static", exist_ok=True)
    with open("static/sgs_skill.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 全部完成，一共 {len(all_data)} 条")

if __name__ == "__main__":
    main()
