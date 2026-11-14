import requests
import re
import json
import time
import os

BASE_URL = "https://wiki.biligame.com/sgs/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9"
}

def get_page_wikitext(page_name):
    params = {
        "action": "query",
        "titles": page_name,
        "prop": "revisions",
        "rvslots": "*",
        "rvprop": "content",
        "format": "json"
    }
    resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
    data = resp.json()
    pages = data["query"]["pages"]
    for _, page_info in pages.items():
        if "revisions" not in page_info:
            print(f"【{page_name}】没有修订内容，页面不存在！")
            return ""
        wikitext = page_info["revisions"][0]["slots"]["main"]["*"]
        print(f"✅【{page_name}】成功拿到wikitext，长度={len(wikitext)}")
        return wikitext
    return ""

def extract_all_skills(wikitext):
    # 匹配 |任意前缀技能=内容
    pattern = re.compile(r"\|([^=]*技能)=(.*?)(?=\n\||\n\}\})", re.S)
    matches = pattern.findall(wikitext)
    skill_list = []
    for key, val in matches:
        val = val.strip()
        skill_list.append(f"{key}：{val}")
    return skill_list


if __name__ == "__main__":
    test_name = "关羽"
    print(f"\n===== 开始抓取：{test_name} =====")
    wiki_text = get_page_wikitext(test_name)
    if not wiki_text:
        print("获取wiki源码失败！")
        out_data = []
    else:
        skill_list = extract_all_skills(wiki_text)
        print(f"\n解析到全部技能：{skill_list}")
        out_data = [{"name": test_name, "skills": skill_list}]

    os.makedirs("static", exist_ok=True)
    with open("static/sgs_data.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)
    print("\n✅ 写入json完成")
