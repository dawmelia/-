import json

def get_first(arr):
    if not arr:
        return ""
    return arr[0]

def main():
    import requests
    base_url = "https://wiki.sgs.qq.com/api.php"
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
        resp = requests.get(base_url, params=params, timeout=15)
        res = resp.json()
        results = res.get("query", {}).get("results", {})
        if not results:
            break
        for item in results.values():
            printouts = item.get("printouts", {})
            skill = get_first(printouts.get("技能", []))
            hero = get_first(printouts.get("所属武将", []))
            # 跳过武将为空的技能（全局机制、阵法等）
            if not hero or not skill:
                continue
            all_data.append({
                "skill": skill,
                "hero": hero
            })
        offset += 500
        print(f"已拉取 {len(all_data)} 条原始技能")

    # ========== 重点：按武将分组，合并同一个武将的多个技能 ==========
    group_dict = {}
    for row in all_data:
        h = row["hero"]
        s = row["skill"]
        if h not in group_dict:
            group_dict[h] = []
        if s not in group_dict[h]:
            group_dict[h].append(s)
    # 转成App需要的数组格式
    out_list = []
    for hero_name, skill_list in group_dict.items():
        out_list.append({
            "name": hero_name,
            "skills": skill_list
        })

    # 输出到 static/sgs_data.json
    out_path = "static/sgs_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out_list, f, ensure_ascii=False, indent=2)
    print(f"✅ 完成！一共 {len(out_list)} 名武将，文件写入：{out_path}")

if __name__ == "__main__":
    main()
