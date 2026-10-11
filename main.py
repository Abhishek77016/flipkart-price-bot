import re, json, time, html
import requests, schedule
from bs4 import BeautifulSoup

TOKEN = "8880334697:AAEXs3tCa1hw3C0QS7nyCU7hhn-Srpr9WWU"
CHAT_ID = "8668506846"

MIN_P, MAX_P = 30000, 40000
PAGES = 3
MAX_PER_RUN = 15
DB_FILE = "prices.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-IN,en;q=0.9",
}
SEARCH = ("https://www.flipkart.com/search?q=mobile+phones"
          f"&p%5B%5D=facets.price_range.from%3D{MIN_P}"
          f"&p%5B%5D=facets.price_range.to%3D{MAX_P}&page={{}}")

SKIP = ("add to compare", "coming soon", "sponsored", "assured",
        "bestseller", "off", "free delivery", "bank offer")


def load_db():
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False)


def nums(text):
    return [int(x.replace(",", "")) for x in re.findall(r"₹\s?([\d,]{4,8})", text)]


def get_name(a, text):
    if a.get("title"):
        return a["title"]
    img = a.find("img")
    if img and img.get("alt"):
        return img["alt"]
    for l in text.split("\n"):
        low = l.lower()
        if len(l) > 10 and "₹" not in l and not any(s in low for s in SKIP):
            return l
    return "Phone"


def get_phones():
    found = {}
    for pg in range(1, PAGES + 1):
        try:
            r = requests.get(SEARCH.format(pg), headers=HEADERS, timeout=20)
            print("Page", pg, "status:", r.status_code)
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print("Page error:", e)
            continue
        for a in soup.find_all("a", href=re.compile(r"/p/itm")):
            link = "https://www.flipkart.com" + a["href"].split("?")[0]
            if link in found:
                continue
            box = a
            for _ in range(5):
                box = box.parent
                if box is None:
                    break
                if "₹" in box.get_text():
                    break
            if box is None:
                continue
            text = box.get_text("\n", strip=True)
            prices = [p for p in nums(text) if MIN_P <= p <= MAX_P]
            if not prices:
                continue
            off = re.search(r"(\d+)%\s*off", text)
            found[link] = {
                "name": get_name(a, text),
                "price": prices[0],
                "off": off.group(1) + "%" if off else "-",
            }
        time.sleep(3)
    print("कुल फ़ोन मिले:", len(found))
    return found


def get_offers(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        lines = BeautifulSoup(r.text, "html.parser").get_text("\n", strip=True).split("\n")
        keys = ("Bank Offer", "Exchange", "No Cost EMI", "Cashback")
        out = [l for l in lines if any(k in l for k in keys) and len(l) < 160]
        return list(dict.fromkeys(out))[:4]
    except Exception:
        return []


def send(p, url, old=None):
    offers = get_offers(url)
    msg = f"📱 <b>{html.escape(p['name'])}</b>\n💰 कीमत: <b>₹{p['price']:,}</b>"
    if old and old > p["price"]:
        msg += f"  ⬇️ (पहले ₹{old:,}, ₹{old - p['price']:,} कम)"
    msg += f"\n🏷 डिस्काउंट: {p['off']}"
    if offers:
        msg += "\n\n🎁 <b>ऑफर:</b>\n" + "\n".join("• " + html.escape(o) for o in offers)
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [[{"text": "🛒 Flipkart पर खोलें", "url": url}]]
            },
        },
        timeout=15,
    )
    print("✅" if r.ok else "❌", p["name"], "" if r.ok else r.text)
    time.sleep(3)
    return r.ok


def check():
    print("फ़ोन चेक हो रहे हैं...")
    db, sent = load_db(), 0
    for url, p in get_phones().items():
        old = db.get(url)
        if (old is None or p["price"] < old) and sent < MAX_PER_RUN:
            if send(p, url, old):
                db[url] = p["price"]
                sent += 1
    save_db(db)
    print(f"कुल {sent} मैसेज भेजे")


check()
schedule.every(60).minutes.do(check)
print("🚀 ट्रैकर चालू है, हर 60 मिनट में चेक करेगा...")
while True:
    schedule.run_pending()
    time.sleep(30)
