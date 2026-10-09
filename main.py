import os
import time
import requests
import schedule
from bs4 import BeautifulSoup

# Railway Environment Variables से डेटा उठाएगा
TELEGRAM_TOKEN = os.getenv("690a36f7219a058fd824ecdd5317378edc27e122")
CHAT_ID = os.getenv("8668506846")
GPLINKS_API_TOKEN = os.getenv("GPLINKS_API_TOKEN", "YOUR_GPLINKS_API_TOKEN_HERE")

PRODUCTS = [
    {
        "name": "Apple iPhone 15 (Black, 128 GB)",
        "url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac2b7f9d0b41"
    }
]

def shorten_with_gplinks(long_url):
    if GPLINKS_API_TOKEN == "YOUR_GPLINKS_API_TOKEN_HERE":
        return long_url
    
    api_url = f"https://gplinks.in/api?api={GPLINKS_API_TOKEN}&url={long_url}"
    try:
        response = requests.get(api_url, timeout=10).json()
        if response.get("status") == "success":
            return response.get("shortenedUrl")
    except Exception as e:
        print("❌ URL Shorten karne me error aaya:", e)
    return long_url

def check_and_send_all_deals():
    print("\n[Multi-Tracker] Sabhi products ka price check kiya ja raha hai...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    for item in PRODUCTS:
        url = item["url"]
        backup_name = item["name"]

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            title_elem = soup.find('span', {'class': 'VU-LmD'}) or soup.find('h1')
            price_elem = soup.find('div', {'class': 'Nx9bqj C3v44M'}) or soup.find('div', {'class': 'Nx9bqj'})

            earning_link = shorten_with_gplinks(url)

            if title_elem and price_elem:
                title = title_elem.get_text().strip()
                price = price_elem.get_text().strip()
                message = f"🚨 LOOT DEAL ALERT! 🚨\n\n📌 Product: {title}\n💰 Price: {price}\n🔗 Buy Link: {earning_link}"
            else:
                message = f"🚨 LOOT DEAL ALERT! 🚨\n\n📌 Product: {backup_name}\n🔗 Check Deal Here: {earning_link}"

            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": CHAT_ID, "text": message}
            requests.post(telegram_url, data=payload)
            print(f"✅ Sent: {backup_name} (Link Shortened)")

            time.sleep(3)

        except Exception as e:
            print(f"❌ Error in {backup_name}:", e)

# पहली बार तुरंत रन करने के लिए
check_and_send_all_deals()

# हर 30 मिनट में ऑटोमैटिक चेक करेगा
schedule.every(30).minutes.do(check_and_send_all_deals)

print("\n🚀 Multi-Product Bot chalu ho gaya hai! Har 30 minute me deals bhejega...")

# 24 घंटे लगातार चालू रखने के लिए लूप
while True:
    schedule.run_pending()
    time.sleep(1)
