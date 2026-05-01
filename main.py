import time
import requests

# =========================
# CONFIG
# =========================

WEBHOOK_URL = "EEEEEE"

# Role to ping on updates (optional)
ROLE_ID = "1234567890"  # set to None if not used

UNIVERSE_IDS = [
    5132638887,
    # add more universe IDs
]

POLL_INTERVAL = 60

# =========================
# STATE STORAGE
# =========================

state = {}

# =========================
# WEBHOOK SENDER
# =========================

def send(embed):
    payload = {
        "content": f"<@&{ROLE_ID}>" if ROLE_ID else None,
        "embeds": [embed]
    }

    # remove null content if no role
    if not ROLE_ID:
        payload.pop("content")

    requests.post(WEBHOOK_URL, json=payload)

# =========================
# ROBLOX API
# =========================

def get_game(universe_id):
    url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
    return requests.get(url).json()["data"][0]

def get_products(universe_id):
    url = f"https://develop.roblox.com/v1/universes/{universe_id}/developerproducts"
    return requests.get(url).json().get("data", [])

# =========================
# SMART DIFF ENGINE
# =========================

def diff_products(old, new):
    changes = []

    old_map = {p["id"]: p for p in old}
    new_map = {p["id"]: p for p in new}

    # New products
    for pid, p in new_map.items():
        if pid not in old_map:
            changes.append(("NEW", p, None))

    # Removed products
    for pid, p in old_map.items():
        if pid not in new_map:
            changes.append(("REMOVED", p, None))

    # Updated products
    for pid, p in new_map.items():
        if pid in old_map:
            old_p = old_map[pid]

            if p["price"] != old_p["price"]:
                changes.append(("PRICE", p, old_p))

            # heuristic rename detection
            if p["name"] != old_p["name"]:
                changes.append(("RENAME", p, old_p))

    return changes

# =========================
# EMBED BUILDER
# =========================

def make_embed(title, desc, color):
    return {
        "title": title,
        "description": desc,
        "color": color,
        "footer": {"text": "Roblox Monitor • Multi-Game Tracker"},
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

# =========================
# MAIN LOOP
# =========================

while True:
    try:
        for universe_id in UNIVERSE_IDS:

            game = get_game(universe_id)
            products = get_products(universe_id)

            if universe_id not in state:
                state[universe_id] = {
                    "last_update": None,
                    "products": []
                }

            last_update = state[universe_id]["last_update"]
            last_products = state[universe_id]["products"]

            # =========================
            # GAME UPDATE DASHBOARD
            # =========================

            if last_update and game["updated"] != last_update:
                send(make_embed(
                    "🚀 Game Update Detected",
                    f"**Universe:** `{universe_id}`\n"
                    f"**Time:** `{game['updated']}`",
                    0x00ff99
                ))

            state[universe_id]["last_update"] = game["updated"]

            # =========================
            # SMART PRODUCT DIFF
            # =========================

            changes = diff_products(last_products, products)

            for change_type, new_p, old_p in changes:

                if change_type == "NEW":
                    send(make_embed(
                        "🆕 New Dev Product",
                        f"**{new_p['name']}**\nPrice: `{new_p['price']} R$`\nGame: `{universe_id}`",
                        0x3498db
                    ))

                elif change_type == "REMOVED":
                    send(make_embed(
                        "🗑️ Dev Product Removed",
                        f"**{old_p['name']}** was removed\nGame: `{universe_id}`",
                        0xff5555
                    ))

                elif change_type == "PRICE":
                    send(make_embed(
                        "💲 Price Change",
                        f"**{new_p['name']}**\n"
                        f"`{old_p['price']} → {new_p['price']} R$`\n"
                        f"Game: `{universe_id}`",
                        0xffcc00
                    ))

                elif change_type == "RENAME":
                    send(make_embed(
                        "✏️ Product Renamed",
                        f"`{old_p['name']} → {new_p['name']}`\nGame: `{universe_id}`",
                        0x9b59b6
                    ))

            state[universe_id]["products"] = products

        time.sleep(POLL_INTERVAL)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
