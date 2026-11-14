import requests
import re
import json
import time
import os

# 三国杀Bwiki主站
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
            print(f"【{page_name}】没有修订内容")
            return ""
        wikitext = page_info["revisions"][0]["slots"]["main"]["*"]
        return wikitext
    return ""

def extract_skills(wikitext):
    # 匹配 |技能1=xxx |技能2=xxx
    pattern = re.compile(r"\|技能\s*(\d+)\s*=(.*?)(?=\|\w+=|\n\}\})", re.S)
    matches = pattern.findall(wikitext)
    skills = []
    for _, skill_text in matches:
        s = skill_text.strip()
        if s:
            skills.append(s)
    return skills


if __name__ == "__main__":
    # 先只测试抓刘备
    test_name = "刘备"
    print(f"开始抓取：{test_name}")
    wiki_text = get_page_wikitext(test_name)
    if not wiki_text:
        print("获取wiki源码失败！")
    else:
        print("成功拿到页面源码长度：", len(wiki_text))
        skill_list = extract_skills(wiki_text)
        print("解析到技能：", skill_list)

        out_data = [
            {
                "name": test_name,
                "skills": skill_list
            }
        ]
        os.makedirs("static", exist_ok=True)
        with open("static/sgs_data.json", "w", encoding="utf-8") as f:
            json.dump(out_data, f, ensure_ascii=False, indent=2)
        print("写入json完成")
