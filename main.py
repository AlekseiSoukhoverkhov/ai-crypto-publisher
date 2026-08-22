import os
import re
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from google import genai
from huggingface_hub import InferenceClient
import telebot
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# ==========================================
# CONFIGURATION AND TOKENS
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

TG_BOT_TOKEN_EN = os.getenv("TG_BOT_TOKEN_EN")
CHAT_ID_EN = os.getenv("CHAT_ID_EN", "@finxten")

TG_BOT_TOKEN_RU = os.getenv("TG_BOT_TOKEN_RU")
CHAT_ID_RU = os.getenv("CHAT_ID_RU", "@finxten_ru")

# Branded signatures for FINXTEN
SIGNATURE_RU = "\n\n✨ Have a great day, FINXTEN wishes your finances — X10! 🚀"
SIGNATURE_EN = "\n\n✨ Have a great day, FINXTEN wishes your finances — X10! 🚀"

print("⚙️ Initializing FINXTEN (Bilingual auto-posting)...")
ai_client = genai.Client(api_key=GEMINI_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

bot_en = telebot.TeleBot(TG_BOT_TOKEN_EN)
bot_ru = telebot.TeleBot(TG_BOT_TOKEN_RU)


def clean_html(raw_html):
    """Clean HTML tags from RSS descriptions"""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return ' '.join(cleantext.split())


def get_real_crypto_prices():
    """Fetch real market data via CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            btc_price = data['bitcoin']['usd']
            btc_change = round(data['bitcoin']['usd_24h_change'], 2)
            eth_price = data['ethereum']['usd']
            eth_change = round(data['ethereum']['usd_24h_change'], 2)
            
            return f"BTC: ${btc_price:,.2f} ({btc_change:+}%), ETH: ${eth_price:,.2f} ({eth_change:+}% )"
    except Exception as e:
        print(f"⚠️ Error fetching quotes: {e}")
    
    return "Exchange rate data is updating."


def get_latest_crypto_news():
    """Parse fresh news from international RSS sources"""
    rss_sources = [
        "https://cointelegraph.com/rss",
        "https://decrypt.co/feed"
    ]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    extracted_news = []

    for url in rss_sources:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall('.//item')[:4]:
                    title_elem = item.find('title')
                    desc_elem = item.find('description')
                    
                    title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                    desc = clean_html(desc_elem.text) if desc_elem is not None and desc_elem.text else ""
                    
                    if title:
                        extracted_news.append(f"• {title}: {desc[:200]}")
        except Exception as e:
            print(f"⚠️ Error reading RSS {url}: {e}")

    if not extracted_news:
        return "Latest news is loading..."
    
    return "\n\n".join(extracted_news[:6])


def generate_daily_report():
    today_date = datetime.now().strftime("%d.%m.%Y")
    print(f"\n📊 Generating expert digests for {today_date}...")

    real_prices = get_real_crypto_prices()
    real_news_feed = get_latest_crypto_news()

    # --- 1. GENERATION FOR THE RUSSIAN CHANNEL (PROMPT IN ENGLISH, OUTPUT IN RUSSIAN) ---
    prompt_ru = (
        f"You are the Editor-in-Chief of FINXTEN. Your audience wants to understand professional slang. Write your response entirely in Russian.\n"
        f"Today is {today_date}.\n\n"
        f"QUOTES:\n{real_prices}\n\n"
        f"LATEST NEWS:\n{real_news_feed}\n\n"
        "PRESENTATION RULES:\n"
        "1. Use correct financial and crypto terms (TradFi, tokenization, derivatives, ETF, volatility, staking, futures, etc.).\n"
        "2. MANDATORY: For every complex term, immediately provide a short, clear explanation in parentheses or as a simple clarification in the same sentence (e.g.: 'TradFi (classic banks and exchanges)', 'Tokenization (transferring real assets to digital form on the blockchain)').\n"
        "3. Retell ONLY facts from the list above.\n\n"
        "POST STRUCTURE:\n"
        "• ☕️ Header with date\n"
        "• 📊 **Market Status**: Briefly about BTC and ETH with an analytical comment.\n"
        "• 📰 **Main Events**: 2-3 key news items with professional terms and their immediate explanations.\n"
        "• 🎯 **Summary**: One concise concluding sentence.\n"
        "Total text volume up to 800 characters, use emojis and paragraphs.\n\n"
        "AT THE VERY END of the response, on a new line, write an English prompt for a 3D illustration without text and logos.\n"
        "PROMPT: <conceptual 3D render representing financial markets and technology, clean design, glowing digital charts, no text, no words, no titles, no watermarks, no logos, 8k resolution>"
    )

    # --- 2. GENERATION FOR THE ENGLISH CHANNEL ---
    prompt_en = (
        f"You are the Editor-in-Chief of FINXTEN. Create a concise, professional crypto digest in English.\n"
        f"Today is {today_date}.\n\n"
        f"MARKET PRICES:\n{real_prices}\n\n"
        f"LATEST NEWS:\n{real_news_feed}\n\n"
        "RULES:\n"
        "1. Use professional crypto/fintech terminology (TradFi, tokenization, derivatives, ETF, volatility, etc.) with brief clear explanations.\n"
        "2. Base the post strictly on the facts provided above.\n\n"
        "STRUCTURE:\n"
        "• ☕️ Header with date\n"
        "• 📊 **Market Overview**: Brief BTC and ETH overview with insight.\n"
        "• 📰 **Top News**: 2-3 key stories with concise context.\n"
        "• 🎯 **Takeaway**: 1 summary sentence.\n"
        "Keep total length under 800 characters. Use Markdown bolding and clear paragraphs."
    )

    try:
        print("🤖 Requesting Gemini (Russian channel version)...")
        res_ru = ai_client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt_ru
        )
        full_text_ru = res_ru.text

        if "PROMPT:" in full_text_ru:
            post_ru, image_prompt = full_text_ru.split("PROMPT:", 1)
            post_ru = post_ru.strip()
            image_prompt = image_prompt.strip()
        else:
            post_ru = full_text_ru.strip()
            image_prompt = "Conceptual 3D render of financial market charts, neon crypto coins, clean layout, no text, no logos, 8k"

        print("🤖 Requesting Gemini (English channel version)...")
        res_en = ai_client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt_en
        )
        post_en = res_en.text.strip()

        caption_ru = post_ru + SIGNATURE_RU
        caption_en = post_en + SIGNATURE_EN

        print(f"✅ Texts are ready!\n\nPrompt for FLUX:\n{image_prompt}\n")

    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return

    # --- 3. IMAGE GENERATION VIA FLUX ---
    print("🎨 Generating unified cover via FLUX.1...")
    image_path = "daily_cover.jpg"
    try:
        image = hf_client.text_to_image(
            image_prompt,
            model="black-forest-labs/FLUX.1-schnell"
        )
        image.save(image_path)
        print("✅ Illustration successfully created!")
    except Exception as e:
        print(f"❌ Error generating image via FLUX: {e}")
        return

    # --- 4. PUBLISHING TO ENGLISH CHANNEL (@finxten) ---
    print(f"🚀 Publishing to English channel ({CHAT_ID_EN})...")
    try:
        with open(image_path, "rb") as photo:
            bot_en.send_photo(
                chat_id=CHAT_ID_EN,
                photo=photo,
                caption=caption_en[:1024],
                parse_mode="Markdown"
            )
        print(f"🔥 POST IN {CHAT_ID_EN} PUBLISHED!")
    except Exception as e:
        print(f"❌ Error sending to {CHAT_ID_EN}: {e}")

    # --- 5. PUBLISHING TO RUSSIAN CHANNEL (@finxten_ru) ---
    print(f"🚀 Publishing to Russian channel ({CHAT_ID_RU})...")
    try:
        with open(image_path, "rb") as photo:
            bot_ru.send_photo(
                chat_id=CHAT_ID_RU,
                photo=photo,
                caption=caption_ru[:1024],
                parse_mode="Markdown"
            )
        print(f"🔥 POST IN {CHAT_ID_RU} PUBLISHED!")
    except Exception as e:
        print(f"❌ Error sending to {CHAT_ID_RU}: {e}")


if __name__ == "__main__":
    generate_daily_report()