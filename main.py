import os
import time
import re
import requests
from bs4 import BeautifulSoup
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Wczytaj dane z .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Rejestrowanie godziny startu
start_time = datetime.now()
print(f"[BOT] Uruchomiono o: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

seen_urls = set()
olx_url = "https://www.olx.pl/elektronika/telefony/smartfony-telefony-komorkowe/iphone/?search%5Border%5D=created_at:desc"

@bot.event
async def on_ready():
    print(f"[DISCORD] Zalogowano jako: {bot.user}")
    scrape_olx.start()

@tasks.loop(seconds=30)
async def scrape_olx():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sprawdzam nowe ogłoszenia...")

    try:
        # --- Selenium setup ---
        chrome_driver_path = "/usr/bin/chromedriver"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(olx_url)

        # Poczekaj na załadowanie najnowszych ogłoszeń
        time.sleep(3)

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, "html.parser")
        listings = soup.select('[data-cy="l-card"]')[:20]

        new_offers = []

        for listing in listings:
            link_tag = listing.find("a", href=True)
            if not link_tag:
                continue

            link = "https://www.olx.pl" + link_tag["href"]
            if link in seen_urls:
                continue

            location = listing.select_one("[data-testid='location-date']")
            time_text = location.text.strip() if location else ""

            if "dzisiaj" in time_text.lower():
                # Wyciągnij godzinę HH:MM z tekstu za pomocą regex
                match = re.search(r'(\d{2}:\d{2})', time_text)
                if not match:
                    print(f"[UWAGA] Nie znaleziono godziny w tekście: '{time_text}'")
                    continue
                time_str = match.group(1)

                try:
                    offer_time = datetime.strptime(
                        datetime.now().strftime("%Y-%m-%d") + " " + time_str,
                        "%Y-%m-%d %H:%M"
                    )
                    print(f"[DEBUG] Ogłoszenie z {time_str} → offer_time: {offer_time.strftime('%H:%M:%S')} | start_time: {start_time.strftime('%H:%M:%S')}")
                    if offer_time < start_time:
                        print(f"[POMINIĘTO] Ogłoszenie z {offer_time.strftime('%H:%M:%S')} < start_time ({start_time.strftime('%H:%M:%S')})")
                        continue
                except Exception as e:
                    print(f"[UWAGA] Błąd parsowania czasu: '{time_text}' ({e})")
                    continue
            else:
                print(f"[POMINIĘTO] Ogłoszenie nie jest z dzisiaj: {time_text}")
                continue

            seen_urls.add(link)

            title_tag = listing.find("h6") or listing.find("h5") or listing.find("h4") or listing.find("h3")
            price = listing.select_one("[data-testid='ad-price']")

            print(f"[NOWE] Dodano nowe ogłoszenie: {link}")

            new_offers.append({
                "Tytuł": title_tag.text.strip() if title_tag else "(Brak tytułu)",
                "Cena": price.text.strip() if price else "Brak",
                "Lokalizacja": location.text.strip() if location else "Brak",
                "Link": link,
                "CzasPublikacji": offer_time  # dodana data publikacji
            })
        if new_offers:
            channel = bot.get_channel(CHANNEL_ID)
            for offer in new_offers:
                # Formatowanie daty publikacji
                data_str = offer["CzasPublikacji"].strftime("%d.%m.%Y, %H:%M")

                msg = (
                    f"📱 **{offer['Tytuł']}**\n"
                    f"💰 Cena: {offer['Cena']}\n"
                    f"📍 Lokalizacja: {offer['Lokalizacja'].split('-')[0].strip()}\n"
                    f"🕒 Data ogłoszenia: {data_str}\n"
                    f"🔗 [Zobacz ogłoszenie]({offer['Link']})"
                )
                await channel.send(msg)

    except Exception as e:
        print("[BŁĄD] Błąd podczas scrapowania:", e)

bot.run(DISCORD_TOKEN)
