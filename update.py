import json, urllib.request, xml.etree.ElementTree as ET
CH = "UCx-Eai2_M-tvcAaKdwha6cg"
URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CH}"
ns = {"a": "http://www.w3.org/2005/Atom", "y": "http://www.youtube.com/xml/schemas/2015"}
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
new = [{"id": e.find("y:videoId", ns).text, "title": e.find("a:title", ns).text}
       for e in root.findall("a:entry", ns)]
try: old = json.load(open("videos.json", encoding="utf-8"))
except Exception: old = []
seen, out = set(), []
for v in new + old:          # नए पहले, पुराने बाद में (history जमा होती रहती है)
    if v["id"] not in seen:
        seen.add(v["id"]); out.append(v)
json.dump(out[:200], open("videos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("videos:", len(out[:200]))
