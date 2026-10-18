import os, re, json, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

NEWS_URL = "https://www.mvr.bg/veliko-tarnovo"
KEYWORDS = r"регистрационен номер|номер по избор|\bЕА\b|електрическ"
SEEN_FILE = "seen.json"
TOPIC = os.environ["NTFY_TOPIC"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
}

def fetch(url):
    r = requests.get(url, timeout=30, headers=HEADERS)
    if r.status_code == 200:
        return r.text
    print("Директно:", r.status_code, "- пробвам през прокси")
    r = requests.get("https://r.jina.ai/" + url, timeout=60,
                     headers={"X-Return-Format": "html"})
    r.raise_for_status()
    return r.text

soup = BeautifulSoup(fetch(NEWS_URL), "html.parser")

found = {}
for a in soup.find_all("a", href=True):
    title = " ".join(a.get_text().split())
    if len(title) > 15 and re.search(KEYWORDS, title, re.I):
        found[urljoin(NEWS_URL, a["href"])] = title

print(f"Намерени съвпадения: {len(found)}")

first_run = not os.path.exists(SEEN_FILE)
seen = set() if first_run else set(json.load(open(SEEN_FILE)))

for url, title in found.items():
    if url not in seen and not first_run:
        requests.post(
            f"https://ntfy.sh/{TOPIC}",
            data=title.encode("utf-8"),
            headers={"Title": "Нова новина: номера ЕА".encode("utf-8"),
                     "Click": url, "Priority": "high"},
        )
        print("Изпратено:", title)

json.dump(sorted(seen | set(found)), open(SEEN_FILE, "w"), ensure_ascii=False, indent=1)
