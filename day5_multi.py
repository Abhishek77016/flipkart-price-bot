import requests
import schedule
import time
from bs4 import BeautifulSoup

# ⚠️ ध्यान दें: अपने टोकन और चैट आईडी को हमेशा गुप्त रखें!
TELEGRAM_TOKEN = "8880334697:AAEXs3tCa1hw3C0QS7nyCU7hhn-Srpr9WWU"
CHAT_ID = "-5496951936"

# 💰 अपना GPLinks का API Token यहाँ डालें (GPLinks.com पर अकाउंट बनाने के बाद Tools -> Quick Link या API सेक्शन में मिलेगा)
GPLINKS_API_TOKEN = os.getenv ("690a36f7219a058fd824ecdd5317378edc27e122")
import os

PRODUCTS = [
    {
        "name": "Apple iPhone 15 (Black, 128 GB)",
        "url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac2010dd1579"
    },
    {
        "name": "Apple AirPods (3rd Gen)",
        "url": "https://www.flipkart.com/apple-airpods-3rd-generation-magsafe-charging-case-bluetooth-headset/p/itm98b5e9f8e4e9f"
    },
    {
        "name": "Apple Watch SE (2nd Gen)",
        "url": "https://www.flipkart.com/apple-watch-se-2nd-gen-gps-40mm-starlight-aluminium-case/p/itm4b29f0322b64b"
    }
]

# 🔗 लिंक को ऑटोमैटिक छोटा करके पैसे कमाने वाला फंक्शन
def shorten_with_gplinks(long_url):
    # अगर आपने अपना टोकन नहीं बदला है, तो असली लिंक ही वापस भेज दे ताकि कोड क्रैश न हो
    if GPLINKS_API_TOKEN == "YOUR_GPLINKS_API_TOKEN_HERE":
        return long_url
        
    api_url = f"https://gplinks.in{GPLINKS_API_TOKEN}&url={long_url}"
    try:
        response = requests.get(api_url, timeout=10).json()
        if response.get("status") == "success":
            return response.get("shortenedUrl") # छोटा किया हुआ लिंक (कमाने वाला लिंक)
    except Exception as e:
        print("❌ URL Shorten karne me error aaya:", e)
    return long_url # अगर कोई एरर आए तो असली लिंक भेज दें ताकि काम न रुके

def check_and_send_all_deals():
    print("\n[Multi-Tracker] Sabhi products ka price check kiya ja raha hai...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    for item in PRODUCTS:
        url = item["url"]
        backup_name = item["name"]

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            title_elem = soup.find('span', {'class': 'VU-LmD'}) or soup.find('h1') or soup.find('span', {'class': '68B04c'})
            price_elem = soup.find('div', {'class': 'Nx9bqj C3v44M'}) or soup.find('div', {'class': 'Nx9bqj'})

            # 🛠️ यहाँ लिंक को छोटा किया जा रहा है जिससे आपकी कमाई होगी
            earning_link = shorten_with_gplinks(url)

            if title_elem and price_elem:
                title = title_elem.get_text().strip()
                price = price_elem.get_text().strip()
                message = f"🚨 LOOT DEAL ALERT! 🚨\n\n📱 Product: {title}\n💰 Price: {price}\n\n🛒 Buy Link: {earning_link}"
            else:
                message = f"🚨 LOOT DEAL ALERT! 🚨\n\n📱 Product: {backup_name}\n\n🛒 Check Deal Here: {earning_link}"

            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message}
            requests.post(telegram_url, data=payload)
            print(f"✅ Sent: {backup_name} (Link Shortened)")

            time.sleep(3)

        except Exception as e:
            print(f"❌ Error in {backup_name}:", e)

check_and_send_all_deals()

schedule.every(30).minutes.do(check_and_send_all_deals)

print("\n🚀 Multi-Product Bot chalu ho gaya hai! Har 30 minute me deals bhejega...")

while True:
    schedule.run_pending()
    time.sleep(1)
    
