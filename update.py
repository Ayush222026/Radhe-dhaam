import json, re, sys, urllib.request, xml.etree.ElementTree as ET

CHANNELS = {
    "UCEk1jBxAl6fe-_G37G7huQA": "@bhajanmarg",
    "UCfJj9RnQgW68e-d8gqor_cg": "@bhaktiimarg1m",
}
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9", "Cookie": "CONSENT=YES+1; SOCS=CAI"}
ns = {"a": "http://www.w3.org/2005/Atom", "y": "http://www.youtube.com/xml/schemas/2015"}

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()

def feed(u, ch):
    root = ET.fromstring(get(u))
    return [{"id": e.find("y:videoId", ns).text, "title": e.find("a:title", ns).text, "ch": ch}
            for e in root.findall("a:entry", ns)]

def scrape(u, ch):
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
        out.append({"id": i, "title": title, "ch": ch})
    return out

def fetch_channel(ch, handle):
    srcs = [
        (feed, "https://www.youtube.com/feeds/videos.xml?playlist_id=UU" + ch[2:]),
        (feed, "https://www.youtube.com/feeds/videos.xml?channel_id=" + ch),
        (scrape, "https://www.youtube.com/" + handle + "/shorts"),
        (scrape, "https://www.youtube.com/" + handle + "/videos"),
    ]
    got = []
    for fn, u in srcs:
        try:
            r = fn(u, ch)
            print("OK", u, len(r))
            got += r
            if fn is feed and r:
                break
        except Exception as e:
            print("FAIL", u, e)
    return got

per = [fetch_channel(c, h) for c, h in CHANNELS.items()]
new = []
for i in range(max(len(p) for p in per)):
    for p in per:
        if i < len(p):
            new.append(p[i])
if not new:
    sys.exit("koi source nahi chala")

try: old = json.load(open("videos.json", encoding="utf-8"))
except Exception: old = []
old = [v for v in old if v.get("ch") in CHANNELS]   # purane channel ke video hat jayenge

seen, out = set(), []
for v in new + old:
    if v["id"] not in seen:
        seen.add(v["id"]); out.append(v)
json.dump(out[:200], open("videos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("videos:", len(out[:200]))
