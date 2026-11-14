import requests
import re
import json
import time
import os

BASE_URL = "https://wiki.biligame.com/sgs/api.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_category_members(cat):
    members = []
    cont = ""
    while True:
        p = {"action":"query","list":"categorymembers","cmtitle":cat,"cmnamespace":0,"cmlimit":50,"format":"json"}
        if cont:
            p["cmcontinue"]=cont
        r = requests.get(BASE_URL, params=p, headers=HEADERS, timeout=15).json()
        members.extend([i["title"] for i in r["query"]["categorymembers"]])
        if "continue" in r:
            cont = r["continue"]["cmcontinue"]
            time.sleep(0.8)
        else:
            break
    return members

def fetch_wikitext(title):
    p = {"action":"query","titles":title,"prop":"revisions","rvslots":"*","rvprop":"content","format":"json"}
    r = requests.get(BASE_URL, params=p, headers=HEADERS, timeout=15).json()
    pg = r["query"]["pages"]
    for k in pg:
        return pg[k]["revisions"][0]["slots"]["main"]["*"]
    return ""

def parse(txt, name):
    pat = re.compile(r"\|技能(\d+)=(.*?)(?=\|技能\d+=|\|称号=|\|势力=|\n\}\})", re.S)
    sk = [x[1].strip() for x in pat.findall(txt) if x[1].strip()]
    return {"name":name,"skills":sk}

if __name__=="__main__":
    cats = ["分类:身份模式武将","分类:国战武将"]
    out = []
    for c in cats:
        for t in get_category_members(c):
            w = fetch_wikitext(t)
            d = parse(w,t)
            if d["skills"]:
                out.append(d)
            time.sleep(0.6)
    os.makedirs("static", exist_ok=True)
    with open("static/sgs_data.json","w",encoding="utf-8") as f:
        json.dump(out,f,ensure_ascii=False,indent=2)
