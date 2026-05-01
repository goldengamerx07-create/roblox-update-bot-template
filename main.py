import os
import requests
import discord
import asyncio

# =========================
# CONFIG (ENV VARIABLES)
# =========================

TOKEN = ma5rfQztZsx8BZT-etDfb6DkIBRAv-jAjC665Nfiwj3iAtUFw_PE-vH-OdfWzAiayPLS
CHANNEL_ID = 1499676874740076565
UNIVERSE_ID = int(os.getenv("UNIVERSE_ID"))

# =========================
# DISCORD SETUP
# =========================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# =========================
# STATE STORAGE
# =========================

last_update = None
last_products = {}

# =========================
# ROBLOX API FUNCTIONS
# =========================

def get_game():
    url = f"https://games.roblox.com/v1/games?universeIds={UNIVERSE_ID}"
    r = requests.get(url).json()
    return r["data"][0]

def get_products():
    url = f"https://develop.roblox.com/v1/universes/{UNIVERSE_ID}/developerproducts"
    r = requests.get(url).json()
    return r.get("data", [])

# =========================
# BOT LOGIC
# =========================

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)
    global last_update, last_products

    while True:
        try:
            # -------------------------
            # GAME UPDATE CHECK
            # -------------------------
            game = get_game()

            if last_update and game["updated"] != last_update:
                await channel.send(
                    f"🚀 **Game Updated!**\nTimestamp: `{game['updated']}`"
                )

            last_update = game["updated"]

            # -------------------------
            # DEV PRODUCTS CHECK
            # -------------------------
            products = get_products()
            current = {p["id"]: p for p in products}

            for pid, product in current.items():
                if pid not in last_products:
                    await channel.send(
                        f"🆕 **New Dev Product**\n{product['name']} - {product['price']} Robux"
                    )
                elif product["price"] != last_products[pid]["price"]:
                    await channel.send(
                        f"💲 **Price Changed**\n{product['name']} → {product['price']} Robux"
                    )

            last_products = current

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(60)

# =========================
# START BOT
# =========================

client.run(TOKEN)
