import json, re, sys, requests
from bs4 import BeautifulSoup

BASE = "https://payhip.com/u1789331237461545433587/collection/all"
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    items = {}
    for a in soup.select('a[href*="/b/"]'):
        m = re.search(r"/b/(\w+)", a["href"])
        title = a.get_text(strip=True)
        if not m or not title or m.group(1) in items:
            continue
        pid, node = m.group(1), a
        for _ in range(7):
            node = node.parent
            if node is None:
                break
            ids = set(re.findall(r"/b/(\w+)", str(node)))
            price = re.search(r"\$\s?([\d.,]+)", node.get_text(" "))
            imgs = [i for i in node.find_all("img")
                    if "loading" not in (i.get("src") or "")]
            if imgs and price and len(ids) == 1:
                src = imgs[0].get("data-src") or imgs[0].get("src") or ""
                items[pid] = {"id": pid, "title": title,
                              "price": float(price.group(1).replace(",", "")),
                              "img": src}
                break
    return items


def main():
    allp = {}
    for off in range(0, 1600, 16):
        url = f"{BASE}?&page={off if off else ''}"
        r = requests.get(url, headers=HDR, timeout=30)
        r.raise_for_status()
        found = parse(r.text)
        new = {k: v for k, v in found.items() if k not in allp}
        if not new:
            break
        allp.update(new)
    if not allp:
        print("No products found - keeping old products.json")
        sys.exit(1)
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(list(allp.values()), f, ensure_ascii=False, indent=1)
    print(len(allp), "products saved")


main()
