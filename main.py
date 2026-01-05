import requests, json, os
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

URL = "https://www.shein.in/SHEINVERSE"
BASE = "https://www.shein.in"
DATA_FILE = "data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)"
}

def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHANNEL_ID,
            "text": msg,
            "disable_web_page_preview": False
        }
    )

def scrape():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "lxml")

    products = []
    cards = soup.select("a[href*='/pd/']")

    for a in cards[:25]:
        link = BASE + a.get("href")
        name = a.get_text(strip=True) or "SHEINVERSE Item"

        price_tag = a.find_next("span", {"class": "price"})
        price = price_tag.get_text(strip=True) if price_tag else "Unknown"

        stock = "Out of Stock" if "sold" in a.parent.text.lower() else "In Stock"

        products.append({
            "name": name,
            "link": link,
            "price": price,
            "stock": stock
        })

    return products

def compare(new):
    old = []
    if os.path.exists(DATA_FILE):
        old = json.load(open(DATA_FILE))

    alerts = []

    for n in new:
        o = next((x for x in old if x["link"] == n["link"]), None)

        if not o:
            alerts.append(("🆕 NEW PRODUCT", n))
        else:
            if o["stock"] != n["stock"]:
                alerts.append(("📦 STOCK UPDATE", n))
            if o["price"] != n["price"]:
                alerts.append(("💰 PRICE CHANGE", n))

    json.dump(new, open(DATA_FILE, "w"), indent=2)
    return alerts

def main():
    send("✅ BOT IS WORKING\nChecked at cron interval.")
    
