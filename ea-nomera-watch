import os, re, json, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

NEWS_URL = "https://www.mvr.bg/veliko-tarnovo"
KEYWORDS = r"регистрационен номер|номер по избор|\bЕА\b|електрическ"
SEEN_FILE = "seen.json"
TOPIC = os.environ["NTFY_TOPIC"]

r = requests.get(NEWS_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

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
