import requests
import re
import json
import time
import os

BASE_URL = "https://wiki.biligame.com/sgs/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_category_members(cat_title):
    members = []
    cont = ""
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": cat_title,
            "cmnamespace": 0,
            "cmlimit": 50,
            "format": "json"
        }
        if cont:
            params["cmcontinue"] = cont
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        data = resp.json()
        members.extend([item["title"] for item in data["query"]["categorymembers"]])
        if "continue" in data:
            cont = data["continue"]["cmcontinue"]
            time.sleep(0.8)
        else:
            break
    return members

def fetch_wikitext(title):
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvslots": "*",
        "rvprop": "content",
        "format": "json"
    }
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
    data = resp.json()
    pages = data["query"]["pages"]
    for pid, page_info in pages.items():
        slot = page_info["revisions"][0]["slots"]["main"]
        return slot["*"]
    return ""

def parse_skill(wiki_text):
    # 放宽正则，兼容wiki里各种换行写法
    pattern = re.compile(r"\|技能\s*(\d+)\s*=(.*?)(?=\|技能|\|称号|\|势力|\n\}\})", re.S)
    res = pattern.findall(wiki_text)
    skills = [s[1].strip() for s in res if s[1].strip()]
    return skills

if __name__ == "__main__":
    # 核对！Biligi游戏三国杀wiki的分类原名，确认是这个
    categories = ["Category:身份模式武将", "Category:国战武将"]
    output = []
    for cat in categories:
        print(f"正在抓取分类：{cat}")
        name_list = get_category_members(cat)
        print(f"该分类下共 {len(name_list)} 个页面")
        for name in name_list:
            wikitext = fetch_wikitext(name)
            skill_list = parse_skill(wikitext)
            if skill_list:
                output.append({
                    "name": name,
                    "skills": skill_list
                })
                print(f"✅ {name} 抓到技能：{skill_list}")
            time.sleep(0.6)
    os.makedirs("static", exist_ok=True)
    with open("static/sgs_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n抓取完成！一共抓到 {len(output)} 个武将")
