from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

BOT_TOKEN ="8642824822:AAFJkL2JBDhArA2U8mzk-dY-nsSN9-23VWQ"
API_ID = 39572733
API_HASH = "1569f0ee27b3670dc249794afab35489"
ADMIN_ID = 8622515071

app = Client(
    "deepbot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# -------------------
# INIT FILES
# -------------------

def ensure_files():
    os.makedirs("keys", exist_ok=True)

    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("orders.json"):
        with open("orders.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("products.json"):
        with open("products.json", "w") as f:
            json.dump({}, f)

ensure_files()

# -------------------
# LOAD / SAVE
# -------------------

def load(file):
    with open(file, "r") as f:
        return json.load(f)

def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# -------------------
# USER SYSTEM
# -------------------

def add_user(uid):
    users = load("users.json")

    if uid not in users:
        users.append(uid)
        save("users.json", users)

# -------------------
# KEY SYSTEM
# -------------------

def get_key(product):
    path = f"keys/{product}.txt"

    if not os.path.exists(path):
        return None

    with open(path, "r") as f:
        keys = f.read().splitlines()

    if not keys:
        return None

    key = keys[0]

    with open(path, "w") as f:
        f.write("\n".join(keys[1:]))

    return key

# -------------------
# START
# -------------------

@app.on_message(filters.command("start"))
async def start(client, message):
    add_user(message.from_user.id)

    buttons = [
        [InlineKeyboardButton("🛒 Buy Products", callback_data="products")],
        [InlineKeyboardButton("📦 My Orders", callback_data="orders")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")]
    ]

    await message.reply_text(
        f"🔥 Welcome {message.from_user.first_name}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------
# PRODUCTS
# -------------------

@app.on_callback_query(filters.regex("^products$"))
async def products_menu(client, cq):

    products = load("products.json")

    buttons = []

    for p in products:
        buttons.append([
            InlineKeyboardButton(p, callback_data=f"buy|{p}")
        ])

    await cq.message.edit_text(
        "🛒 Select Product",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------
# BUY
# -------------------

@app.on_callback_query(filters.regex("^buy\\|"))
async def buy_menu(client, cq):

    product = cq.data.split("|")[1]
    products = load("products.json")

    if product not in products:
        return await cq.message.reply_text("❌ Product not found")

    text = f"🔥 {product}\n\n"
    buttons = []

    for duration, price in products[product].items():
        text += f"{duration} = ₹{price}\n"

        buttons.append([
            InlineKeyboardButton(
                f"{duration} - ₹{price}",
                callback_data=f"pay|{product}|{duration}|{price}"
            )
        ])

    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

# -------------------
# PAYMENT
# -------------------

@app.on_callback_query(filters.regex("^pay\\|"))
async def payment(client, cq):

    data = cq.data.split("|")
    product, duration, price = data[1], data[2], data[3]

    buttons = [
        [InlineKeyboardButton("✅ I Have Paid", callback_data=f"done|{product}|{duration}")]
    ]

    await cq.message.reply_photo(
        "qr.jpg",
        caption=f"💳 Pay ₹{price}\n📦 {product}\n⏳ {duration}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# -------------------
# DELIVERY
# -------------------

@app.on_callback_query(filters.regex("^done\\|"))
async def done(client, cq):

    product, duration = cq.data.split("|")[1:3]

    key = get_key(product)

    if not key:
        return await cq.message.reply_text("❌ Out of stock")

    orders = load("orders.json")

    orders.append({
        "user_id": cq.from_user.id,
        "product": product,
        "duration": duration,
        "key": key
    })

    save("orders.json", orders)

    await cq.message.reply_text(f"🔑 YOUR KEY:\n\n{key}")

# -------------------
# PROFILE
# -------------------

@app.on_callback_query(filters.regex("^profile$"))
async def profile(client, cq):
    await cq.message.reply_text(
        f"👤 ID: {cq.from_user.id}\n📛 Name: {cq.from_user.first_name}"
    )

# -------------------
# ORDERS
# -------------------

@app.on_callback_query(filters.regex("^orders$"))
async def orders(client, cq):

    all_orders = load("orders.json")

    user_orders = []

    for o in all_orders:
        if o["user_id"] == cq.from_user.id:
            user_orders.append(o)

    if not user_orders:
        return await cq.message.reply_text("❌ No Orders")

    text = "📦 Orders\n\n"

    for o in user_orders:
        text += f"{o['product']} → {o['key']}\n\n"

    await cq.message.reply_text(text)

# -------------------
# RUN BOT
# -------------------

app.run()
