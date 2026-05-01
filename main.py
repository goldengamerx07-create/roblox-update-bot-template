import requests
import time

# =========================
# CONFIG
# =========================

WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_HERE"
UNIVERSE_ID = 5132638887

# =========================
# STATE
# =========================

last_update = None
last_products = {}

# =========================
# SEND FUNCTION
# =========================

def send(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

# =========================
# ROBLOX API
# =========================

def get_game():
    url = f"https://games.roblox.com/v1/games?universeIds={UNIVERSE_ID}"
    return requests.get(url).json()["data"][0]

def get_products():
    url = f"https://develop.roblox.com/v1/universes/{UNIVERSE_ID}/developerproducts"
    return requests.get(url).json().get("data", [])

# =========================
# LOOP
# =========================

while True:
    try:
        # -------------------------
        # GAME UPDATE CHECK
        # -------------------------
        game = get_game()

        global last_update

        if last_update and game["updated"] != last_update:
            send(f"🚀 **Game Updated!**\n`{game['updated']}`")

        last_update = game["updated"]

        # -------------------------
        # DEV PRODUCTS CHECK
        # -------------------------
        products = get_products()
        current = {p["id"]: p for p in products}

        global last_products

        for pid, product in current.items():
            if pid not in last_products:
                send(f"🆕 **New Dev Product**\n{product['name']} - {product['price']} Robux")
            elif product["price"] != last_products[pid]["price"]:
                send(f"💲 **Price Changed**\n{product['name']} → {product['price']} Robux")

        last_products = current

    except Exception as e:
        print("Error:", e)

    time.sleep(60)
