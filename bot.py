from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

BOT_TOKEN = "8642824822:AAFJkL2JBDhArA2U8mzk-dY-nsSN9-23VWQ"
API_ID = 39572733
API_HASH = "1569f0ee27b3670dc249794afab35489"
ADMIN_ID = 8622515071

app = Client(
"deepbot",
bot_token=BOT_TOKEN,
api_id=API_ID,
api_hash=API_HASH
)

-------------------

FILE FUNCTIONS

-------------------

def load_products():
with open("products.json", "r") as f:
return json.load(f)

def load_users():
with open("users.json", "r") as f:
return json.load(f)

def save_users(data):
with open("users.json", "w") as f:
json.dump(data, f, indent=4)

def load_orders():
with open("orders.json", "r") as f:
return json.load(f)

def save_orders(data):
with open("orders.json", "w") as f:
json.dump(data, f, indent=4)

-------------------

SAVE USER

-------------------

def add_user(user_id):

users = load_users()  

if user_id not in users:  
    users.append(user_id)  
    save_users(users)

-------------------

GET KEY

-------------------

def get_key(product):

file_path = f"keys/{product}.txt"  

if not os.path.exists(file_path):  
    return None  

with open(file_path, "r") as f:  
    keys = f.readlines()  

if len(keys) == 0:  
    return None  

first_key = keys[0].strip()  

with open(file_path, "w") as f:  
    f.writelines(keys[1:])  

return first_key

-------------------

START

-------------------

@app.on_message(filters.command("start"))
async def start(client, message):

add_user(message.from_user.id)  

buttons = [  
    [InlineKeyboardButton("🛒 Buy Products", callback_data="products")],  
    [InlineKeyboardButton("📦 My Orders", callback_data="orders")],  
    [InlineKeyboardButton("👤 My Profile", callback_data="profile")],  
    [InlineKeyboardButton("📞 Support", url="https://t.me/DEEPMODS1")]  
]  

await message.reply_text(  
    f"""

🔥 Welcome {message.from_user.first_name}

✅ Auto Digital Delivery Store
""",
reply_markup=InlineKeyboardMarkup(buttons)
)

-------------------

PRODUCTS

-------------------

@app.on_callback_query(filters.regex("products"))
async def products_menu(client, callback_query):

products = load_products()  

buttons = []  

for product in products:  
    buttons.append([  
        InlineKeyboardButton(  
            product,  
            callback_data=f"buy|{product}"  
        )  
    ])  

buttons.append([  
    InlineKeyboardButton("🔙 Back", callback_data="back")  
])  

await callback_query.message.edit_text(  
    "🛒 Select Product",  
    reply_markup=InlineKeyboardMarkup(buttons)  
)

-------------------

BUY MENU

-------------------

@app.on_callback_query(filters.regex("^buy|"))
async def buy_menu(client, callback_query):

product = callback_query.data.split("|")[1]  

products = load_products()  

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

buttons.append([  
    InlineKeyboardButton("🔙 Back", callback_data="products")  
])  

await callback_query.message.edit_text(  
    text,  
    reply_markup=InlineKeyboardMarkup(buttons)  
)

-------------------

PAYMENT

-------------------

@app.on_callback_query(filters.regex("^pay|"))
async def payment(client, callback_query):

data = callback_query.data.split("|")  

product = data[1]  
duration = data[2]  
price = data[3]  

buttons = [  
    [InlineKeyboardButton(  
        "✅ I Have Paid",  
        callback_data=f"done|{product}|{duration}"  
    )]  
]  

await callback_query.message.reply_photo(  
    photo="qr.jpg",  
    caption=f"""

💳 PAYMENT DETAILS

📦 Product: {product}
⏳ Duration: {duration}
💰 Amount: ₹{price}

After payment click below button.
""",
reply_markup=InlineKeyboardMarkup(buttons)
)

-------------------

AUTO DELIVERY

-------------------

@app.on_callback_query(filters.regex("^done|"))
async def auto_delivery(client, callback_query):

data = callback_query.data.split("|")  

product = data[1]  
duration = data[2]  

key = get_key(product)  

if key is None:  

    await callback_query.message.reply_text(  
        "❌ Product Out Of Stock"  
    )  

    return  

orders = load_orders()  

orders.append({  
    "user_id": callback_query.from_user.id,  
    "product": product,  
    "duration": duration,  
    "key": key  
})  

save_orders(orders)  

await callback_query.message.reply_text(  
    f"""

✅ PAYMENT SUCCESSFUL

📦 Product: {product}
⏳ Duration: {duration}

🔑 YOUR KEY:

{key}

⚠️ Save Your Key Carefully.
"""
)

-------------------

PROFILE

-------------------

@app.on_callback_query(filters.regex("profile"))
async def profile(client, callback_query):

await callback_query.message.reply_text(  
    f"""

👤 USER PROFILE

🆔 ID: {callback_query.from_user.id}
📛 Name: {callback_query.from_user.first_name}
"""
)

-------------------

MY ORDERS

-------------------

@app.on_callback_query(filters.regex("orders"))
async def orders(client, callback_query):

all_orders = load_orders()  

user_orders = []  

for order in all_orders:  

    if order["user_id"] == callback_query.from_user.id:  
        user_orders.append(order)  

if len(user_orders) == 0:  

    await callback_query.message.reply_text(  
        "❌ No Orders Found"  
    )  

    return  

text = "📦 YOUR ORDERS\n\n"  

for order in user_orders:  

    text += f"📦 {order['product']}\n"  
    text += f"🔑 {order['key']}\n\n"  

await callback_query.message.reply_text(text)

-------------------

BROADCAST

-------------------

@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(client, message):

if len(message.command) < 2:  

    await message.reply_text(  
        "Usage:\n/broadcast message"  
    )  

    return  

text = message.text.split(None, 1)[1]  

users = load_users()  

success = 0  

for user in users:  

    try:  
        await client.send_message(user, text)  
        success += 1  
    except:  
        pass  

await message.reply_text(  
    f"✅ Broadcast Sent To {success} Users"  
)

-------------------

USER COUNT

-------------------

@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def users_count(client, message):

users = load_users()  

await message.reply_text(  
    f"👥 Total Users: {len(users)}"  
)

-------------------

BACK BUTTON

-------------------

@app.on_callback_query(filters.regex("back"))
async def back(client, callback_query):

buttons = [  
    [InlineKeyboardButton("🛒 Buy Products", callback_data="products")],  
    [InlineKeyboardButton("📦 My Orders", callback_data="orders")],  
    [InlineKeyboardButton("👤 My Profile", callback_data="profile")]  
]  

await callback_query.message.edit_text(  
    "🔥 Main Menu",  
    reply_markup=InlineKeyboardMarkup(buttons)  
)

-------------------

RUN

-------------------

app.run()
