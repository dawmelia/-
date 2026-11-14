import json
import requests

def get_first(arr):
    if not arr:
        return ""
    return arr[0]

def main():
    base_url = "https://wiki.biligame.com/sgs/api.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    params = {
        "action": "ask",
        "query": "[[Category:技能]]|?技能|?所属武将|?技能类型",
        "format": "json",
        "limit": 500
    }
    offset = 0
    all_data = []
    while True:
        params["offset"] = offset
        try:
            resp = requests.get(base_url, params=params, headers=headers, timeout=20)
            # 先判断状态码，并且打印原始内容方便排查
            print(f"status={resp.status_code}, raw preview: {resp.text[:200]}")
            if resp.status_code != 200:
                print("接口返回非200，停止")
                break
            res = resp.json()
        except Exception as e:
            print("请求/解析异常：", e)
            break
        results = res.get("query", {}).get("results", {})
        if not results:
            break
        for item in results.values():
            printouts = item.get("printouts", {})
            skill = get_first(printouts.get("技能", []))
            hero = get_first(printouts.get("所属武将", []))
            if not hero or not skill:
                continue
            all_data.append({
                "skill": skill,
                "hero": hero
            })
        offset += 500
        print(f"已拉取 {len(all_data)} 条原始技能")

    group_dict = {}
    for row in all_data:
        h = row["hero"]
        s = row["skill"]
        if h not in group_dict:
            group_dict[h] = []
        if s not in group_dict[h]:
            group_dict[h].append(s)
    out_list = []
    for hero_name, skill_list in group_dict.items():
        out_list.append({
            "name": hero_name,
            "skills": skill_list
        })

    out_path = "static/sgs_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_list, f, ensure_ascii=False, indent=2)
    print(f"✅ 完成！一共 {len(out_list)} 名武将，文件写入：{out_path}")

if __name__ == "__main__":
    main()
