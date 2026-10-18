import json, re, sys, urllib.request, xml.etree.ElementTree as ET

CH = "UCx-Eai2_M-tvcAaKdwha6cg"
H = "https://www.youtube.com/@amritvanibypremanandji"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
ns = {"a": "http://www.w3.org/2005/Atom", "y": "http://www.youtube.com/xml/schemas/2015"}

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()

def feed(u):
    root = ET.fromstring(get(u))
    return [{"id": e.find("y:videoId", ns).text, "title": e.find("a:title", ns).text}
            for e in root.findall("a:entry", ns)]

def scrape(u):
    t = get(u).decode("utf-8", "ignore")
    out, seen = [], set()
    for m in re.finditer(r'"videoId":"([\w-]{11})"', t):
        i = m.group(1)
        if i in seen:
            continue
        seen.add(i)
        tm = re.search(r'"(?:text|simpleText)":"([^"]{3,200})"', t[m.end():m.end() + 700])
        title = "प्रवचन"
        if tm:
            try: title = json.loads('"' + tm.group(1) + '"')
            except Exception: pass
        out.append({"id": i, "title": title})
    return out

SOURCES = [
    (feed, "https://www.youtube.com/feeds/videos.xml?playlist_id=UU" + CH[2:]),
    (feed, "https://www.youtube.com/feeds/videos.xml?channel_id=" + CH),
    (scrape, H + "/shorts"),
    (scrape, H + "/videos"),
]
new = []
for fn, u in SOURCES:
    try:
        r = fn(u)
        print("OK", u, len(r))
        new += r
        if fn is feed and r:
            break
    except Exception as e:
        print("FAIL", u, e)
if not new:
    sys.exit("koi source nahi chala")

try: old = json.load(open("videos.json", encoding="utf-8"))
except Exception: old = []
seen, out = set(), []
for v in new + old:
    if v["id"] not in seen:
        seen.add(v["id"]); out.append(v)
json.dump(out[:200], open("videos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("videos:", len(out[:200]))
