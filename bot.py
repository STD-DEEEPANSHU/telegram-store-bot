import asyncio
import logging
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BufferedInputFile

import config
import database as db
import keyboards as kb
from qr_generator import generate_upi_qr

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Bot & Dispatcher
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# FSM States
class BotStates(StatesGroup):
    entering_promo = State()
    entering_custom_paytm = State()
    awaiting_payment_screenshot = State()
    awaiting_direct_order_screenshot = State()
    admin_adding_keys_pkg = State()
    admin_adding_keys_input = State()
    admin_crediting_user_id = State()
    admin_crediting_amount = State()
    admin_creating_promo_code = State()
    admin_creating_promo_reward = State()
    admin_creating_promo_uses = State()
    admin_broadcasting = State()
    admin_sending_key_userid = State()
    admin_sending_key_text = State()
    admin_sending_key_for_req = State()
    admin_editing_price_input = State()

# ==========================================
# 🌟 /start & MAIN NAVIGATION
# ==========================================

def format_duration(pkg_or_days) -> str:
    if isinstance(pkg_or_days, dict):
        if pkg_or_days.get("duration_label"):
            return pkg_or_days["duration_label"]
        days = pkg_or_days.get("duration_days", 1)
    else:
        days = pkg_or_days

    try:
        f = float(days)
        if f == 0.25:
            return "6 Hours"
        if f < 1.0 or f in (0.0, 0.5):
            return "12 Hours"
        return f"{int(f)} Days"
    except (ValueError, TypeError):
        return str(days)

def get_welcome_text() -> str:
    return (
        f"⚡ <b>{config.STORE_NAME}</b> ⚡\n"
        f"<i>{config.STORE_TAGLINE}</i>\n\n"
        "👋 <b>Welcome to the Store!</b>\n"
        "<i>Instant automated delivery & 24/7 active services.</i>\n\n"
        "❖ <b>NAVIGATION MENU</b> ❖\n"
        "┣ 🛒 <b>Product Store</b> ➔ <i>Instant key delivery</i>\n"
        "┣ 💰 <b>Add Balance</b> ➔ <i>UPI • Crypto • bKash</i>\n"
        "┣ 👤 <b>My Profile</b> ➔ <i>Account & live wallet</i>\n"
        "┣ 🔑 <b>All History</b> ➔ <i>Past orders & keys</i>\n"
        "┣ 👥 <b>Referral System</b> ➔ <i>Earn 15% bonus</i>\n"
        "┣ 🎵 <b>STD Music APK</b> ➔ <i>Official music app download</i>\n"
        "┣ ⬇️ <b>Download Files</b> ➔ <i>Verified safe APKs</i>\n"
        "┣ 🎬 <b>Tutorials</b> ➔ <i>Bot usage & video guide</i>\n"
        "┗ 🌐 <b>Helpdesk</b> ➔ <i>Live customer support</i>\n\n"
        "✨ <b>Fast • Automated • 100% Reliable</b>"
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "User"

    # Check for referral payload
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
        except ValueError:
            referrer_id = None

    db.get_or_create_user(user_id, username, full_name, referrer_id)
    await message.answer(get_welcome_text(), reply_markup=kb.get_main_menu_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "menu_home")
async def cb_menu_home(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.edit_text(get_welcome_text(), reply_markup=kb.get_main_menu_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(get_welcome_text(), reply_markup=kb.get_main_menu_keyboard(), parse_mode="HTML")
    await call.answer()

# ==========================================
# 👤 USER PROFILE & PROMO CODE
# ==========================================

@dp.callback_query(F.data == "menu_profile")
async def cb_menu_profile(call: types.CallbackQuery):
    user = db.get_user(call.from_user.id)
    if not user:
        user = db.get_or_create_user(call.from_user.id, call.from_user.username or "", call.from_user.full_name)

    bal_inr = user["wallet_balance"]
    bal_usd = bal_inr * config.INR_TO_USD_RATE
    spent_inr = user["total_spent"]
    spent_usd = spent_inr * config.INR_TO_USD_RATE

    profile_text = (
        "👤 <b>USER PROFILE DASHBOARD</b> 👤\n\n"
        "┏━━ 👤 <b>ACCOUNT INFO</b> ━━┓\n"
        f"┣ 👤 User: <b>{user['full_name']}</b>\n"
        f"┣ 🆔 User ID: <code>{user['user_id']}</code>\n"
        f"┣ 👑 Rank: <b>{user['rank']}</b>\n"
        f"┗ 📅 Joined: <code>{user['joined_date']}</code>\n\n"
        "┏━━ 💰 <b>WALLET BALANCE</b> ━━┓\n"
        f"┗ 🪙 Available Funds: <b>₹{bal_inr:.2f}</b> (~ ${bal_usd:.2f})\n\n"
        "┏━━ 📊 <b>ACTIVITY STATS</b> ━━┓\n"
        f"┣ 🛒 Orders Completed: <b>{user['orders_completed']}</b>\n"
        f"┣ 💸 Total Spent: <b>₹{spent_inr:.2f}</b> (~ ${spent_usd:.2f})\n"
        f"┗ 👥 Total Referrals: <b>{user['total_referrals']}</b>"
    )

    try:
        await call.message.edit_text(profile_text, reply_markup=kb.get_profile_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(profile_text, reply_markup=kb.get_profile_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "redeem_promo")
async def cb_redeem_promo(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.entering_promo)
    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 BACK", callback_data="menu_profile")]
    ])
    await call.message.edit_text("🎟️ <b>Please enter your VIP / Promo redeem code below:</b>", reply_markup=back_kb, parse_mode="HTML")
    await call.answer()

@dp.message(BotStates.entering_promo)
async def process_promo_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    success, msg = db.claim_promo(message.from_user.id, code)
    await state.clear()
    
    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="👤 Go to Profile", callback_data="menu_profile")],
        [types.InlineKeyboardButton(text="🔙 Main Menu", callback_data="menu_home")]
    ])
    await message.answer(msg, reply_markup=back_kb)

# ==========================================
# 👥 REFERRAL / AFFILIATE SYSTEM
# ==========================================

@dp.callback_query(F.data == "menu_referral")
async def cb_menu_referral(call: types.CallbackQuery):
    user = db.get_user(call.from_user.id)
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{call.from_user.id}"

    comm_inr = user["total_commission"] if user else 0.0
    comm_usd = comm_inr * config.INR_TO_USD_RATE
    invited = user["total_referrals"] if user else 0

    ref_text = (
        "👥 <b>AFFILIATE & PARTNERS</b> 👥\n"
        f"<i>Earn Passive Income with {config.STORE_NAME}</i>\n\n"
        "Invite your friends and earn instant cash rewards on every key purchase they make!\n\n"
        "┏━━ 🎁 <b>COMMISSION RATE</b> ━━┓\n"
        f"┗ 💰 Flat <b>{config.REFERRAL_PERCENT}% Bonus</b> credited automatically to your wallet.\n\n"
        "┏━━ 📊 <b>YOUR STATS</b> ━━┓\n"
        f"┣ 👥 Friends Invited: <b>{invited} users</b>\n"
        f"┗ 💰 Total Commission: <b>₹{comm_inr:.2f}</b> (~ ${comm_usd:.2f})\n\n"
        "┏━━ 🔗 <b>YOUR UNIQUE LINK</b> ━━┓\n"
        f"👉 <code>{ref_link}</code>\n"
        "<i>(Tap to copy)</i>\n\n"
        "Share this link with your friends to start earning immediately!"
    )

    try:
        await call.message.edit_text(ref_text, reply_markup=kb.get_referral_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(ref_text, reply_markup=kb.get_referral_keyboard(), parse_mode="HTML")
    await call.answer()

# ==========================================
# 🎬 TUTORIALS & ⬇️ DOWNLOADS
# ==========================================

@dp.callback_query(F.data == "menu_tutorials")
async def cb_menu_tutorials(call: types.CallbackQuery):
    tut_text = (
        "🎬 <b>BOT GUIDE & TUTORIALS</b> 🎬\n"
        f"<i>How to Use {config.STORE_NAME} Bot</i>\n\n"
        "🚀 <b>STEP-BY-STEP GUIDE</b> ━━\n\n"
        "1️⃣ <b>Deposit Funds</b>\n"
        "┗ Tap <b>Add Balance</b> and pay via Paytm QR, Binance Pay, or bKash.\n\n"
        "2️⃣ <b>Choose Panel</b>\n"
        "┗ Tap <b>Product Store</b>, choose your OS category, brand, and validity.\n\n"
        "3️⃣ <b>Instant Delivery</b>\n"
        "┗ Your license key and installation APK link are delivered in seconds!\n\n"
        "4️⃣ <b>Download APKs & Configs</b>\n"
        "┗ Use <b>Download Files</b> to get clean updates and bypass scripts.\n\n"
        "Need further assistance? Check out our Support Center anytime."
    )
    try:
        await call.message.edit_text(tut_text, reply_markup=kb.get_tutorials_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(tut_text, reply_markup=kb.get_tutorials_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "menu_downloads")
async def cb_menu_downloads(call: types.CallbackQuery):
    down_text = (
        "📦 <b>PREMIUM DOWNLOAD VAULT</b> 📦\n"
        "<i>Official Files & Verified APKs</i>\n\n"
        "All updated files and tools are hosted on our dedicated private channel.\n\n"
        "┏━━ 📦 <b>WHAT'S INSIDE</b> ━━┓\n"
        "┣ ⚡ <b>Latest APK Updates</b> — Fresh builds & fixes\n"
        "┣ 🛡️ <b>100% Virus-Free</b> — Clean & verified safe\n"
        "┣ 🌸 <b>Configs & Scripts</b> — High performance files\n"
        "┗ 📌 <b>Full Installation Guides</b> — Easy setup steps\n\n"
        "✅ <b>Tap the button below to access downloads:</b>"
    )
    try:
        await call.message.edit_text(down_text, reply_markup=kb.get_downloads_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(down_text, reply_markup=kb.get_downloads_keyboard(), parse_mode="HTML")
    await call.answer()

# ==========================================
# 🔑 ALL HISTORY
# ==========================================

@dp.callback_query(F.data == "menu_history")
async def cb_menu_history(call: types.CallbackQuery):
    orders = db.get_user_orders(call.from_user.id)
    if not orders:
        msg = (
            "🔑 <b>ALL ORDERS & KEYS HISTORY</b> 🔑\n\n"
            "<i>You haven't purchased any license keys yet.</i>\n\n"
            "Browse 🛒 <b>Product Store</b> to buy your first key!"
        )
    else:
        msg = "🔑 <b>YOUR PAST ORDERS & KEYS</b> 🔑\n\n"
        for o in orders:
            msg += (
                f"┏━━ 📦 <b>{o.get('brand_name') or 'License'} ({format_duration(o.get('duration_days', 0))})</b> ━━┓\n"
                f"┣ 🆔 Order Ref: <code>{o['order_ref']}</code>\n"
                f"┣ 💰 Paid: ₹{o['amount_inr']:.2f} ({o['payment_method']})\n"
                f"┣ 🔑 Key: <code>{o['license_key']}</code>\n"
                f"┗ 📅 Date: {o['created_at']}\n\n"
            )

    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])
    try:
        await call.message.edit_text(msg, reply_markup=back_kb, parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(msg, reply_markup=back_kb, parse_mode="HTML")
    await call.answer()

# ==========================================
# 🎁 LUDO SPIN / LUCKY DICE
# ==========================================

@dp.callback_query(F.data == "menu_ludo")
async def cb_menu_ludo(call: types.CallbackQuery):
    user_id = call.from_user.id
    can_claim, time_left = db.can_claim_ludo(user_id)
    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

    if not can_claim:
        await call.message.edit_text(
            f"⏳ <b>LUDO SPIN COOLDOWN</b> ⏳\n\n"
            f"You have already rolled today!\n"
            f"Next spin available in: <b>{time_left}</b>\n\n"
            "Come back tomorrow for more free balance!",
            reply_markup=back_kb,
            parse_mode="HTML"
        )
        await call.answer()
        return

    await call.message.delete()
    dice_msg = await bot.send_dice(chat_id=call.message.chat.id, emoji="🎲")
    
    # Wait for the Telegram dice roll animation
    await asyncio.sleep(3.5)
    
    dice_val = dice_msg.dice.value
    # Rewards mapping
    rewards = {
        6: 10.0,
        5: 5.0,
        4: 3.0,
        3: 2.0,
        2: 1.0,
        1: 1.0
    }
    prize = rewards.get(dice_val, 1.0)
    db.record_ludo_claim(user_id, prize)
    user = db.get_user(user_id)

    win_text = (
        f"🎲 <b>LUDO SPIN RESULT: {dice_val}!</b> 🎲\n\n"
        f"🎉 <b>Congratulations!</b> You won <b>₹{prize:.2f}</b> free wallet balance!\n\n"
        f"💰 <b>Updated Live Balance:</b> ₹{user['wallet_balance']:.2f}\n\n"
        f"<i>Roll again after 24 hours!</i>"
    )
    await bot.send_message(chat_id=call.message.chat.id, text=win_text, reply_markup=back_kb, parse_mode="HTML")

# ==========================================
# 🛒 PRODUCT STORE (CATEGORIES ➔ BRANDS ➔ PACKAGES)
# ==========================================

@dp.callback_query(F.data == "menu_store")
async def cb_menu_store(call: types.CallbackQuery):
    cats = db.get_categories()
    text = (
        "🛒 <b>PRODUCT PANELS VAULT</b> 🛒\n"
        "<i>Select Operating System / Platform</i>\n\n"
        "✅ <b>Choose your target category below:</b>"
    )
    try:
        await call.message.edit_text(text, reply_markup=kb.get_categories_keyboard(cats), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(text, reply_markup=kb.get_categories_keyboard(cats), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("cat_"))
async def cb_select_category(call: types.CallbackQuery):
    cat_id = int(call.data.split("_")[1])
    brands = db.get_brands_by_category(cat_id)
    
    # Get category name
    cats = db.get_categories()
    cat_name = next((c["name"] for c in cats if c["id"] == cat_id), "PANELS")

    if not brands:
        text = f"🛒 <b>{cat_name}</b>\n\n<i>No brands are currently available in this category.</i>"
        back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔙 BACK TO PANELS", callback_data="menu_store")]
        ])
        await call.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")
        await call.answer()
        return

    text = (
        f"🛒 <b>{cat_name}</b>\n"
        "<i>Select Desired Panel Brand</i>\n\n"
        "✅ <b>Available Panel Brands:</b>"
    )
    await call.message.edit_text(text, reply_markup=kb.get_brands_keyboard(brands, cat_id), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("brand_"))
async def cb_select_brand(call: types.CallbackQuery):
    brand_id = int(call.data.split("_")[1])
    brand = db.get_brand(brand_id)
    packages = db.get_packages_by_brand(brand_id)

    if not packages:
        text = f"🛒 <b>{brand['name']}</b>\n\n<i>No packages are available for this brand right now.</i>"
        back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔙 BACK TO PANELS", callback_data=f"cat_{brand['category_id']}")]
        ])
        await call.message.edit_text(text, reply_markup=back_kb, parse_mode="HTML")
        await call.answer()
        return

    text = (
        f"🛒 <b>{brand['name']}</b>\n"
        "<i>Instant Automated License Delivery</i>\n\n"
    )

    for p in packages:
        stock = db.get_stock_count(p["id"])
        usd = p["price_inr"] * config.INR_TO_USD_RATE
        status_icon = "🟢 In Stock" if stock > 0 else "🔴 Out of Stock"
        dur_str = format_duration(p)
        text += (
            f"📦 <b>Package: {dur_str}</b>\n"
            f"┣ 💰 Price: <b>₹{p['price_inr']:.2f} (~ ${usd:.2f})</b>\n"
            f"┣ 🖥️ HWID: {p['hwid_device']} Device\n"
            f"┗ {status_icon}\n\n"
        )

    text += "✅ <b>Select package below to purchase:</b>"
    await call.message.edit_text(text, reply_markup=kb.get_packages_keyboard(packages, brand_id), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("outofstock_"))
async def cb_outofstock(call: types.CallbackQuery):
    await call.answer("❌ This package is currently out of stock! Please try another or contact support.", show_alert=True)

# ==========================================
# 💳 BUY / DIRECT CHECKOUT UPI QR
# ==========================================

@dp.callback_query(F.data.startswith("buy_"))
async def cb_buy_package(call: types.CallbackQuery):
    pkg_id = int(call.data.split("_")[1])
    pkg = db.get_package(pkg_id)
    user_id = call.from_user.id
    user = db.get_user(user_id)

    stock = db.get_stock_count(pkg_id)
    if stock <= 0:
        await call.answer("❌ Out of stock! Please check back later.", show_alert=True)
        return

    price = pkg["price_inr"]
    brand_name = pkg["brand_name"]
    days = pkg["duration_days"]
    dur_str = format_duration(pkg)

    # 1. User has sufficient balance in wallet -> Instant Delivery!
    if user and user["wallet_balance"] >= price:
        key = db.pop_license_key(pkg_id, user_id)
        if not key:
            await call.answer("❌ Out of stock right now!", show_alert=True)
            return

        db.update_user_balance(user_id, -price)
        order_ref = f"ORD{user_id}B{pkg_id}T{int(time.time())}"
        db.create_completed_order(order_ref, user_id, pkg_id, price, key, "WALLET_BALANCE")

        success_text = (
            "🎉 <b>PURCHASE SUCCESSFUL!</b> 🎉\n\n"
            f"📦 <b>Package:</b> {brand_name} ({dur_str})\n"
            f"💰 <b>Amount Paid:</b> ₹{price:.2f} (Deducted from Wallet)\n"
            f"🆔 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
            f"🔑 <b>YOUR LICENSE KEY:</b>\n"
            f"<code>{key}</code>\n"
            "<i>(Tap to copy)</i>\n\n"
            f"⬇️ <b>Download Files:</b> {config.DOWNLOAD_CHANNEL_URL}\n\n"
            "✨ <i>Thank you for shopping with us!</i>"
        )
        back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="🔑 View in History", callback_data="menu_history")],
            [types.InlineKeyboardButton(text="🛒 Back to Store", callback_data="menu_store")]
        ])
        await call.message.edit_text(success_text, reply_markup=back_kb, parse_mode="HTML")
        await call.answer()
        return

    # 2. Wallet balance is less -> Show Direct Checkout QR Code!
    order_ref = f"PTM{user_id}B{pkg_id}T{int(time.time())}"
    qr_bytes = generate_upi_qr(price, order_ref)
    qr_file = BufferedInputFile(qr_bytes.read(), filename="checkout_qr.png")

    caption = (
        "🛒 <b>DIRECT CHECKOUT QR</b> 🛒\n"
        "<i>Scan & Pay with Any UPI App</i>\n\n"
        f"📦 <b>Package:</b> {brand_name} ({dur_str})\n"
        f"💵 <b>Due Amount:</b> ₹{price:.2f}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
        "⚡ <b>Supported:</b> Paytm • GPay • PhonePe • BHIM\n"
        "📡 <b>Auto-detecting payment in real time...</b>\n"
        "⚠️ <i>QR expires in 3 minutes. Do not close!</i>\n"
        "✨ <b>Key will be delivered instantly on payment.</b>"
    )

    await call.message.delete()
    qr_msg = await bot.send_photo(
        chat_id=call.message.chat.id,
        photo=qr_file,
        caption=caption,
        reply_markup=kb.get_direct_checkout_keyboard(order_ref, pkg_id),
        parse_mode="HTML"
    )
    await call.answer()

    # Schedule 3-minute QR timeout watcher
    asyncio.create_task(qr_timeout_watcher(call.message.chat.id, qr_msg.message_id, order_ref, f"{brand_name} ({dur_str})"))

async def qr_timeout_watcher(chat_id: int, message_id: int, order_ref: str, package_name: str):
    await asyncio.sleep(180)  # 3 minutes
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM orders WHERE order_ref = ?", (order_ref,))
    row = c.fetchone()
    conn.close()
    if not row or row["status"] != "COMPLETED":
        try:
            timeout_text = (
                f"⏳ <b>Payment Timed Out!</b> ────────────────\n"
                f"📦 <b>Product:</b> {package_name}\n"
                f"🆔 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
                "<i>This checkout QR has expired (3 mins limit). Please generate a fresh checkout if needed.</i>"
            )
            back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="🛒 Back to Store", callback_data="menu_store")]
            ])
            await bot.send_message(chat_id=chat_id, text=timeout_text, reply_markup=back_kb, parse_mode="HTML")
        except Exception:
            pass


@dp.callback_query(F.data.startswith("confirm_pay_"))
async def cb_confirm_payment(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    order_ref = parts[2]
    pkg_id = int(parts[3])
    pkg = db.get_package(pkg_id)
    if not pkg:
        await call.answer("❌ Invalid package!", show_alert=True)
        return

    await state.set_state(BotStates.awaiting_direct_order_screenshot)
    await state.update_data(
        order_ref=order_ref,
        pkg_id=pkg_id,
        price=pkg["price_inr"],
        brand_name=pkg["brand_name"],
        duration_days=pkg["duration_days"]
    )

    cancel_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_store")]
    ])
    await call.message.answer(
        "📸 <b>Please send your Payment Screenshot now:</b>\n\n"
        f"📦 <b>Package:</b> {pkg['brand_name']} ({format_duration(pkg['duration_days'])})\n"
        f"💵 <b>Amount Paid:</b> ₹{pkg['price_inr']:.2f}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
        "<i>Make sure the UTR / Transaction ID is clearly visible in the screenshot.</i>",
        reply_markup=cancel_kb,
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(BotStates.awaiting_direct_order_screenshot, F.photo)
async def process_direct_order_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    order_ref = data.get("order_ref", f"ORD{message.from_user.id}T{int(time.time())}")
    pkg_id = data.get("pkg_id")
    price = data.get("price", 0.0)
    brand_name = data.get("brand_name", "License")
    duration_days = data.get("duration_days", 1)
    file_id = message.photo[-1].file_id

    req_id = db.record_direct_order_request(message.from_user.id, pkg_id, price, order_ref, file_id)
    await state.clear()

    await message.answer(
        "✅ <b>Payment Screenshot Received!</b>\n\n"
        f"📦 <b>Product:</b> {brand_name} ({format_duration(duration_days)})\n"
        f"💵 <b>Amount:</b> ₹{price:.2f}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
        "⚡ <b>Status: Pending Admin Verification</b>\n"
        "<i>Your payment screenshot has been sent to Admin. As soon as Admin approves it, your license key will be delivered automatically right here!</i>",
        reply_markup=kb.get_main_menu_keyboard(),
        parse_mode="HTML"
    )

    # Notify Admins
    username_str = f"@{message.from_user.username}" if message.from_user.username else "No username"
    admin_caption = (
        f"🛒 <b>NEW ORDER #{req_id} PENDING KEY DELIVERY</b>\n\n"
        f"👤 <b>Buyer:</b> {message.from_user.full_name} ({username_str})\n"
        f"🆔 <b>User ID:</b> <code>{message.from_user.id}</code> (tap to copy)\n"
        f"📦 <b>Package:</b> {brand_name} ({format_duration(duration_days)})\n"
        f"💵 <b>Amount Due:</b> ₹{price:.2f}\n"
        f"🔖 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
        f"💡 <b>To deliver key, send:</b>\n<code>/sendkey {message.from_user.id} &lt;KEY_HERE&gt;</code>\n\n"
        "<i>Or tap below to enter key or reject:</i>"
    )
    for aid in config.ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=aid,
                photo=file_id,
                caption=admin_caption,
                reply_markup=kb.get_direct_order_action_keyboard(req_id),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to alert admin {aid}: {e}")

# ==========================================
# 💰 ADD BALANCE / DEPOSIT GATEWAYS
# ==========================================

@dp.callback_query(F.data == "menu_deposit")
async def cb_menu_deposit(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    dep_text = (
        "💸 <b>DEPOSIT FUNDS</b> 💸\n"
        "<i>Instant Automated Wallet Credit</i>\n\n"
        "Choose your payment gateway below:\n\n"
        "┏━━ 💳 <b>SUPPORTED METHODS</b> ━━┓\n"
        "┣ 📲 <b>Paytm UPI</b> ➔ <i>Instant QR (GPay/PhonePe/Paytm)</i>\n"
        "┣ 🪙 <b>Binance Pay</b> ➔ <i>Zero fee USDT transfer</i>\n"
        f"┗ 🇧🇩 <b>bKash (BD)</b> ➔ <i>Taka payment (100 INR = 120 Tk)</i>\n\n"
        "✅ <b>All transactions are encrypted and verified automatically.</b>\n"
        "👉 <b>Tap your preferred method below:</b>"
    )
    try:
        await call.message.edit_text(dep_text, reply_markup=kb.get_deposit_methods_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.delete()
        await call.message.answer(dep_text, reply_markup=kb.get_deposit_methods_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "dep_paytm")
async def cb_dep_paytm(call: types.CallbackQuery):
    text = (
        "💵 <b>— PAYTM UPI DEPOSIT —</b> 💵\n\n"
        "Select amount to deposit:"
    )
    await call.message.edit_text(text, reply_markup=kb.get_paytm_amounts_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("paytm_amt_"))
async def cb_paytm_amount(call: types.CallbackQuery, state: FSMContext):
    amt_str = call.data.replace("paytm_amt_", "")
    user_id = call.from_user.id

    if amt_str == "custom":
        await state.set_state(BotStates.entering_custom_paytm)
        await call.message.edit_text(
            "✏️ <b>Enter custom deposit amount in ₹ INR (e.g. 150):</b>",
            reply_markup=kb.get_cancel_deposit_keyboard(),
            parse_mode="HTML"
        )
        await call.answer()
        return

    amount = float(amt_str)
    await send_paytm_qr(call.message, user_id, amount)
    await call.answer()

@dp.message(BotStates.entering_custom_paytm)
async def process_custom_paytm_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount < 10:
            await message.answer("⚠️ Minimum deposit amount is ₹10. Please enter a valid amount:")
            return
    except ValueError:
        await message.answer("⚠️ Please enter a valid number (e.g. 250):")
        return

    await state.clear()
    await send_paytm_qr(message, message.from_user.id, amount)

async def send_paytm_qr(message_or_call_msg, user_id: int, amount: float):
    order_ref = f"DEP{user_id}T{int(time.time())}"
    qr_bytes = generate_upi_qr(amount, order_ref)
    qr_file = BufferedInputFile(qr_bytes.read(), filename="deposit_qr.png")

    caption = (
        "💵 <b>PAYTM UPI DEPOSIT QR</b> 💵\n"
        "<i>Scan & Pay with Any UPI App</i>\n\n"
        f"💵 <b>Amount:</b> ₹{amount:.2f}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_ref}</code>\n\n"
        "⚡ <b>Supported:</b> Paytm • GPay • PhonePe • BHIM\n"
        "📸 <b>After Payment:</b> Send your payment screenshot right here in chat to get verified and credited promptly!"
    )
    confirm_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📸 Upload Screenshot", callback_data=f"upload_sc_PAYTM_{amount}_{order_ref}")],
        [types.InlineKeyboardButton(text="🔙 Back", callback_data="dep_paytm")]
    ])
    await bot.send_photo(chat_id=user_id, photo=qr_file, caption=caption, reply_markup=confirm_kb, parse_mode="HTML")

@dp.callback_query(F.data == "dep_binance")
async def cb_dep_binance(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.awaiting_payment_screenshot)
    await state.update_data(method="BINANCE", amount=0.0, order_ref=f"BIN{call.from_user.id}T{int(time.time())}")

    text = (
        "🪙 <b>BINANCE PAY DEPOSIT</b> 🪙\n"
        "<i>Fast Zero-Fee Crypto Deposit</i>\n\n"
        "Send your USDT payment directly to our official Binance Pay:\n\n"
        f"👉 <b>Binance Pay ID:</b> <code>{config.BINANCE_PAY_ID}</code> <i>(Tap to copy)</i>\n\n"
        "📸 <b>AFTER PAYMENT:</b>\n"
        "Upload or send the payment screenshot right here.\n"
        "⚡ Admin will verify and credit your wallet promptly."
    )
    await call.message.edit_text(text, reply_markup=kb.get_cancel_deposit_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "dep_bkash")
async def cb_dep_bkash(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(BotStates.awaiting_payment_screenshot)
    await state.update_data(method="BKASH", amount=0.0, order_ref=f"BKS{call.from_user.id}T{int(time.time())}")

    text = (
        "🇧🇩 <b>bKash DEPOSIT (TAKA)</b> 🇧🇩\n"
        "<i>Bangladesh Direct Payment</i>\n\n"
        "💵 <b>Conversion Rate: 100 INR = 120 Taka (1.20 Tk / ₹)</b>\n\n"
        "👉 Send payment to our personal bKash number:\n"
        f"👉 <code>{config.BKASH_NUMBER}</code> <i>(Tap to copy number)</i>\n\n"
        "📸 <b>AFTER SENDING:</b>\n"
        "Upload or send the payment screenshot right here.\n"
        "⚡ Admin will verify and credit equivalent INR to your wallet!"
    )
    await call.message.edit_text(text, reply_markup=kb.get_cancel_deposit_keyboard(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("upload_sc_"))
async def cb_upload_sc(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    method = parts[2]
    amount = float(parts[3])
    order_ref = parts[4]

    await state.set_state(BotStates.awaiting_payment_screenshot)
    await state.update_data(method=method, amount=amount, order_ref=order_ref)
    await call.message.answer("📸 Please send your payment screenshot image now:")
    await call.answer()

@dp.message(BotStates.awaiting_payment_screenshot, F.photo)
async def process_payment_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    method = data.get("method", "UPI")
    amount = data.get("amount", 0.0)
    order_ref = data.get("order_ref", f"MAN{message.from_user.id}T{int(time.time())}")
    file_id = message.photo[-1].file_id

    req_id = db.record_deposit_request(message.from_user.id, method, amount, order_ref, file_id)
    await state.clear()

    await message.answer(
        "✅ <b>Screenshot Received!</b>\n\n"
        f"🆔 Request ID: <code>#{req_id}</code>\n"
        f"💳 Method: <b>{method}</b>\n\n"
        "⚡ Your payment screenshot has been forwarded to Admin for verification. "
        "Once verified, your wallet will be credited automatically!",
        reply_markup=kb.get_main_menu_keyboard(),
        parse_mode="HTML"
    )

    # Notify Admins
    admin_caption = (
        f"🔔 <b>NEW DEPOSIT REQUEST #{req_id}</b>\n\n"
        f"👤 User: {message.from_user.full_name} (<code>{message.from_user.id}</code>)\n"
        f"💳 Method: {method}\n"
        f"💰 Expected Amount: ₹{amount:.2f}\n"
        f"🆔 Ref: <code>{order_ref}</code>"
    )
    for aid in config.ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=aid,
                photo=file_id,
                caption=admin_caption,
                reply_markup=kb.get_deposit_action_keyboard(req_id),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin {aid}: {e}")

# ==========================================
# 👑 ADMIN PANEL
# ==========================================

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    stats = db.get_stats()
    admin_text = (
        "👑 <b>ADMINISTRATION DASHBOARD</b> 👑\n\n"
        f"👥 Total Users: <b>{stats['users']}</b>\n"
        f"💰 Total User Balances: <b>₹{stats['balance']:.2f}</b>\n"
        f"🛒 Completed Orders: <b>{stats['orders']}</b>\n"
        f"💵 Total Revenue: <b>₹{stats['revenue']:.2f}</b>\n"
        f"📦 Total Active Keys in Stock: <b>{stats['stock']}</b>\n\n"
        "Choose an action below:"
    )
    await message.answer(admin_text, reply_markup=kb.get_admin_main_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("appr_dep_"))
async def cb_admin_approve_deposit(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        await call.answer("Unauthorized", show_alert=True)
        return
    req_id = int(call.data.replace("appr_dep_", ""))
    req = db.approve_deposit(req_id)
    if not req:
        await call.answer("Already processed!", show_alert=True)
        return

    await call.message.edit_caption(caption=call.message.caption + "\n\n✅ <b>APPROVED BY ADMIN</b>", parse_mode="HTML")
    # Notify user
    try:
        await bot.send_message(
            chat_id=req["user_id"],
            text=(
                f"🎉 <b>DEPOSIT APPROVED!</b> 🎉\n\n"
                f"Your deposit of <b>₹{req['amount_inr']:.2f}</b> has been verified and added to your wallet.\n\n"
                "Enjoy shopping in 🛒 <b>Product Store</b>!"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await call.answer("Deposit Approved & Credited!", show_alert=True)

@dp.callback_query(F.data.startswith("rejc_dep_"))
async def cb_admin_reject_deposit(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        await call.answer("Unauthorized", show_alert=True)
        return
    req_id = int(call.data.replace("rejc_dep_", ""))
    req = db.reject_deposit(req_id)
    if not req:
        await call.answer("Already processed!", show_alert=True)
        return

    await call.message.edit_caption(caption=call.message.caption + "\n\n❌ <b>REJECTED BY ADMIN</b>", parse_mode="HTML")
    # Notify user
    try:
        await bot.send_message(
            chat_id=req["user_id"],
            text="❌ <b>Deposit Request Rejected.</b>\nYour payment screenshot could not be verified. Please contact support.",
            parse_mode="HTML"
        )
    except Exception:
        pass
    await call.answer("Deposit Rejected!", show_alert=True)

# Admin: Manual Key Delivery (/sendkey command)
@dp.message(Command("sendkey"))
async def cmd_sendkey(message: types.Message):
    if message.from_user.id not in config.ADMIN_IDS:
        return

    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "ℹ️ <b>Usage:</b> <code>/sendkey &lt;user_id&gt; &lt;key&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/sendkey 123456789 CTB-ABCD-1234</code>",
            parse_mode="HTML"
        )
        return

    try:
        target_uid = int(parts[1].strip())
    except ValueError:
        await message.answer("❌ Invalid User ID! It must be numeric (e.g. <code>123456789</code>).", parse_mode="HTML")
        return

    key_str = parts[2].strip()
    order_info = db.deliver_manual_key(target_uid, key_str)
    pkg = order_info.get("pkg")
    pkg_str = f"{pkg['brand_name']} ({format_duration(pkg['duration_days'])})" if pkg else "VIP Panel License"

    buyer_text = (
        "🎉 <b>PAYMENT APPROVED & LICENSE DELIVERED!</b> 🎉\n\n"
        f"📦 <b>Package:</b> {pkg_str}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_info['order_ref']}</code>\n\n"
        f"🔑 <b>YOUR LICENSE KEY:</b>\n"
        f"<code>{key_str}</code>\n"
        "<i>(Tap to copy)</i>\n\n"
        f"⬇️ <b>Download Channel:</b> {config.DOWNLOAD_CHANNEL_URL}\n"
        f"🌐 <b>Support:</b> {config.SUPPORT_LINK}\n\n"
        "✨ <i>Thank you for purchasing! Key is also saved in your All History menu.</i>"
    )

    sent = True
    try:
        await bot.send_message(chat_id=target_uid, text=buyer_text, parse_mode="HTML")
    except Exception as e:
        sent = False
        logger.error(f"Failed to deliver key to {target_uid}: {e}")

    if sent:
        await message.answer(
            f"✅ <b>Key Successfully Delivered!</b>\n\n"
            f"👤 <b>Buyer:</b> <code>{target_uid}</code>\n"
            f"📦 <b>Package:</b> {pkg_str}\n"
            f"🔑 <b>Delivered Key:</b> <code>{key_str}</code>\n"
            f"🔖 <b>Order Ref:</b> <code>{order_info['order_ref']}</code>",
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f"⚠️ <b>Order recorded in database, but failed to DM user <code>{target_uid}</code>.</b>\n"
            f"(User might have blocked or not started the bot).\n"
            f"🔑 Key: <code>{key_str}</code>",
            parse_mode="HTML"
        )

# Admin: Click "Send Key Now" on Order Notification
@dp.callback_query(F.data.startswith("send_key_req_"))
async def cb_admin_send_key_prompt(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        await call.answer("Unauthorized", show_alert=True)
        return

    req_id = int(call.data.replace("send_key_req_", ""))
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM direct_order_requests WHERE id = ? AND status = 'PENDING'", (req_id,))
    req = c.fetchone()
    conn.close()

    if not req:
        await call.answer("This order has already been processed!", show_alert=True)
        return

    await state.set_state(BotStates.admin_sending_key_for_req)
    await state.update_data(req_id=req_id, user_id=req["user_id"])

    await call.message.reply(
        f"📝 <b>Order #{req_id}</b>\n"
        f"👤 <b>Buyer ID:</b> <code>{req['user_id']}</code>\n"
        f"💵 <b>Amount Due:</b> ₹{req['amount_inr']:.2f}\n\n"
        "Send or reply with the <b>License Key</b> to deliver now:",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(BotStates.admin_sending_key_for_req)
async def process_admin_key_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    req_id = data.get("req_id")
    target_uid = data.get("user_id")
    key_str = message.text.strip()
    await state.clear()

    order_info = db.deliver_manual_key(target_uid, key_str, req_id=req_id)
    pkg = order_info.get("pkg")
    pkg_str = f"{pkg['brand_name']} ({format_duration(pkg['duration_days'])})" if pkg else "VIP Panel License"

    buyer_text = (
        "🎉 <b>PAYMENT APPROVED & LICENSE DELIVERED!</b> 🎉\n\n"
        f"📦 <b>Package:</b> {pkg_str}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_info['order_ref']}</code>\n\n"
        f"🔑 <b>YOUR LICENSE KEY:</b>\n"
        f"<code>{key_str}</code>\n"
        "<i>(Tap to copy)</i>\n\n"
        f"⬇️ <b>Download Channel:</b> {config.DOWNLOAD_CHANNEL_URL}\n"
        f"🌐 <b>Support:</b> {config.SUPPORT_LINK}\n\n"
        "✨ <i>Thank you for purchasing! Key is also saved in your All History menu.</i>"
    )

    try:
        await bot.send_message(chat_id=target_uid, text=buyer_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to deliver key to {target_uid}: {e}")

    await message.answer(
        f"✅ <b>ORDER #{req_id} APPROVED & DELIVERED!</b>\n\n"
        f"👤 <b>Buyer:</b> <code>{target_uid}</code>\n"
        f"📦 <b>Product:</b> {pkg_str}\n"
        f"🔑 <b>Delivered Key:</b> <code>{key_str}</code>\n"
        f"👑 <b>Admin:</b> {message.from_user.full_name}",
        parse_mode="HTML"
    )

# Legacy / Direct Order Rejection
@dp.callback_query(F.data.startswith("rejc_ord_"))
async def cb_admin_reject_order(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        await call.answer("Unauthorized", show_alert=True)
        return
    req_id = int(call.data.replace("rejc_ord_", ""))
    req = db.reject_direct_order(req_id)
    if not req:
        await call.answer("Already processed or invalid!", show_alert=True)
        return

    user_id = req["user_id"]
    reject_text = (
        "❌ <b>PAYMENT VERIFICATION FAILED</b>\n\n"
        f"🆔 <b>Order Ref:</b> <code>{req['order_ref']}</code>\n"
        f"💵 <b>Amount:</b> ₹{req['amount_inr']:.2f}\n\n"
        "Your payment screenshot could not be verified by Admin.\n"
        f"If you believe this is an error, please reach out to Support: {config.SUPPORT_LINK}"
    )
    try:
        await bot.send_message(chat_id=user_id, text=reject_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to notify user {user_id}: {e}")

    try:
        await call.message.edit_caption(
            caption=(
                f"❌ <b>ORDER #{req_id} REJECTED</b>\n\n"
                f"👤 Buyer: <code>{user_id}</code>\n"
                f"💵 Amount: ₹{req['amount_inr']:.2f}\n"
                f"🔖 Ref: <code>{req['order_ref']}</code>\n"
                f"👑 Rejected By: {call.from_user.full_name}"
            ),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await call.answer("❌ Order Rejected.", show_alert=True)

# Admin: Add Stock
@dp.callback_query(F.data == "adm_add_keys")
async def cb_adm_add_keys(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, b.name as brand, p.duration_days 
        FROM packages p 
        JOIN brands b ON p.brand_id = b.id
    """)
    pkgs = c.fetchall()
    conn.close()

    text = "📦 <b>Select package ID to add license keys to:</b>\n\n"
    for p in pkgs:
        text += f"ID: <code>{p['id']}</code> ➔ {p['brand']} ({format_duration(p['duration_days'])})\n"
    text += "\nSend the <b>Package ID</b> now:"
    await state.set_state(BotStates.admin_adding_keys_pkg)
    await call.message.answer(text, parse_mode="HTML")
    await call.answer()

@dp.message(BotStates.admin_adding_keys_pkg)
async def process_adm_pkg_id(message: types.Message, state: FSMContext):
    try:
        pkg_id = int(message.text.strip())
    except ValueError:
        await message.answer("Please enter a valid numeric Package ID:")
        return
    await state.update_data(pkg_id=pkg_id)
    await state.set_state(BotStates.admin_adding_keys_input)
    await message.answer("📝 Send the keys now (one key per line):")

@dp.message(BotStates.admin_adding_keys_input)
async def process_adm_keys_list(message: types.Message, state: FSMContext):
    data = await state.get_data()
    pkg_id = data["pkg_id"]
    keys = message.text.strip().split("\n")
    inserted = db.add_keys_bulk(pkg_id, keys)
    await state.clear()
    await message.answer(f"✅ Successfully added <b>{inserted}</b> keys to Package ID {pkg_id}!", parse_mode="HTML")

# Admin: Credit User Balance
@dp.callback_query(F.data == "adm_add_bal")
async def cb_adm_add_bal(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    await state.set_state(BotStates.admin_crediting_user_id)
    await call.message.answer("👤 Enter the Telegram <b>User ID</b> to credit balance:", parse_mode="HTML")
    await call.answer()

@dp.message(BotStates.admin_crediting_user_id)
async def process_adm_user_id(message: types.Message, state: FSMContext):
    try:
        target_uid = int(message.text.strip())
    except ValueError:
        await message.answer("Please enter a valid numeric User ID:")
        return
    await state.update_data(target_uid=target_uid)
    await state.set_state(BotStates.admin_crediting_amount)
    await message.answer(f"💰 Enter amount to credit to <code>{target_uid}</code> in ₹ INR:", parse_mode="HTML")

@dp.message(BotStates.admin_crediting_amount)
async def process_adm_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
    except ValueError:
        await message.answer("Please enter a valid numeric amount:")
        return
    data = await state.get_data()
    target_uid = data["target_uid"]
    db.update_user_balance(target_uid, amount)
    await state.clear()
    await message.answer(f"✅ Successfully credited <b>₹{amount:.2f}</b> to user <code>{target_uid}</code>!", parse_mode="HTML")
    try:
        await bot.send_message(
            chat_id=target_uid,
            text=f"🎁 <b>Admin has credited ₹{amount:.2f} to your wallet!</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

# Admin: Create Promo Code
@dp.callback_query(F.data == "adm_create_promo")
async def cb_adm_create_promo(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    await state.set_state(BotStates.admin_creating_promo_code)
    await call.message.answer("🎟️ Enter new Promo Code name (e.g. <code>SPECIAL100</code>):", parse_mode="HTML")
    await call.answer()

@dp.message(BotStates.admin_creating_promo_code)
async def process_promo_name(message: types.Message, state: FSMContext):
    code = message.text.strip().upper()
    await state.update_data(code=code)
    await state.set_state(BotStates.admin_creating_promo_reward)
    await message.answer(f"💰 Enter reward amount in ₹ INR for code <b>{code}</b>:", parse_mode="HTML")

@dp.message(BotStates.admin_creating_promo_reward)
async def process_promo_reward(message: types.Message, state: FSMContext):
    try:
        reward = float(message.text.strip())
    except ValueError:
        await message.answer("Please enter a valid number:")
        return
    await state.update_data(reward=reward)
    await state.set_state(BotStates.admin_creating_promo_uses)
    await message.answer("👥 Enter maximum number of users who can claim this code:")

@dp.message(BotStates.admin_creating_promo_uses)
async def process_promo_uses(message: types.Message, state: FSMContext):
    try:
        uses = int(message.text.strip())
    except ValueError:
        await message.answer("Please enter an integer:")
        return
    data = await state.get_data()
    db.create_promo(data["code"], data["reward"], uses)
    await state.clear()
    await message.answer(f"✅ Promo Code <code>{data['code']}</code> created for ₹{data['reward']} ({uses} claims max)!", parse_mode="HTML")

# Admin: Broadcast
@dp.callback_query(F.data == "adm_broadcast")
async def cb_adm_broadcast(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    await state.set_state(BotStates.admin_broadcasting)
    await call.message.answer("📢 Send the message (text, photo, or announcement) to broadcast to ALL users:")
    await call.answer()

@dp.message(BotStates.admin_broadcasting)
async def process_broadcast(message: types.Message, state: FSMContext):
    await state.clear()
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = [r["user_id"] for r in c.fetchall()]
    conn.close()

    sent = 0
    await message.answer(f"🚀 Starting broadcast to {len(users)} users...")
    for uid in users:
        try:
            await message.copy_to(chat_id=uid)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass

    await message.answer(f"✅ Broadcast finished! Sent to {sent}/{len(users)} users.")

# ==========================================
# 👑 DYNAMIC ADMIN FEATURES: PRICE & PACKAGE MANAGER
# ==========================================

@dp.callback_query(F.data == "menu_admin_home")
async def cb_menu_admin_home(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    await state.clear()
    stats = db.get_stats()
    admin_text = (
        "👑 <b>ADMINISTRATION DASHBOARD</b> 👑\n\n"
        f"👥 Total Users: <b>{stats['users']}</b>\n"
        f"💰 Total User Balances: <b>₹{stats['balance']:.2f}</b>\n"
        f"🛒 Completed Orders: <b>{stats['orders']}</b>\n"
        f"💵 Total Revenue: <b>₹{stats['revenue']:.2f}</b>\n"
        f"📦 Total Active Keys in Stock: <b>{stats['stock']}</b>\n\n"
        "Choose an action below:"
    )
    try:
        await call.message.edit_text(admin_text, reply_markup=kb.get_admin_main_keyboard(), parse_mode="HTML")
    except Exception:
        await call.message.answer(admin_text, reply_markup=kb.get_admin_main_keyboard(), parse_mode="HTML")
    await call.answer()

# 1. Change Price Flow
@dp.callback_query(F.data == "adm_change_price")
async def cb_adm_change_price(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    cats = db.get_categories()
    text = "💰 <b>CHANGE PACKAGE PRICE</b>\n\nSelect a Category to browse brands & packages:"
    await call.message.edit_text(text, reply_markup=kb.get_admin_categories_keyboard(cats, "adm_cat_price"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("adm_cat_price_"))
async def cb_adm_cat_price(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    cat_id = int(call.data.replace("adm_cat_price_", ""))
    brands = db.get_brands_by_category(cat_id)
    text = "💰 <b>CHANGE PACKAGE PRICE</b>\n\nSelect a Brand:"
    await call.message.edit_text(text, reply_markup=kb.get_admin_brands_keyboard(brands, cat_id, "adm_br_price"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("adm_br_price_"))
async def cb_adm_br_price(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    brand_id = int(call.data.replace("adm_br_price_", ""))
    brand = db.get_brand(brand_id)
    pkgs = db.get_packages_by_brand(brand_id)
    bname = brand["name"] if brand else "Brand"
    text = f"💰 <b>CHANGE PRICE FOR: {bname}</b>\n\nSelect the package you want to change price for:"
    await call.message.edit_text(text, reply_markup=kb.get_admin_packages_keyboard(pkgs, brand_id), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("adm_setprice_pkg_"))
async def cb_adm_setprice_pkg(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    pkg_id = int(call.data.replace("adm_setprice_pkg_", ""))
    pkg = db.get_package(pkg_id)
    if not pkg:
        await call.answer("Package not found!", show_alert=True)
        return

    dur = pkg.get("duration_label") or f"{pkg['duration_days']} Days"
    await state.set_state(BotStates.admin_editing_price_input)
    await state.update_data(pkg_id=pkg_id, brand_name=pkg["brand_name"], duration_str=dur, old_price=pkg["price_inr"])

    prompt_text = (
        f"✏️ <b>EDITING PRICE</b>\n\n"
        f"📦 <b>Product:</b> {pkg['brand_name']}\n"
        f"⏳ <b>Duration:</b> {dur}\n"
        f"💵 <b>Current Price:</b> ₹{pkg['price_inr']:.2f}\n\n"
        "Send the <b>New Price in ₹ INR</b> now (e.g. <code>85</code> or <code>150</code>):"
    )
    cancel_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Cancel", callback_data="adm_change_price")]
    ])
    await call.message.answer(prompt_text, reply_markup=cancel_kb, parse_mode="HTML")
    await call.answer()

@dp.message(BotStates.admin_editing_price_input)
async def process_adm_new_price(message: types.Message, state: FSMContext):
    try:
        new_price = float(message.text.strip())
        if new_price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Please enter a valid positive number for the price (e.g. <code>99</code> or <code>150.00</code>):")
        return

    data = await state.get_data()
    pkg_id = data["pkg_id"]
    brand_name = data["brand_name"]
    duration_str = data["duration_str"]
    old_price = data["old_price"]
    await state.clear()

    db.update_package_price(pkg_id, new_price)

    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💰 Change Another Price", callback_data="adm_change_price")],
        [types.InlineKeyboardButton(text="👑 Back to Admin", callback_data="menu_admin_home")]
    ])

    await message.answer(
        f"✅ <b>PRICE UPDATED SUCCESSFULLY!</b>\n\n"
        f"📦 <b>Package:</b> {brand_name} ({duration_str})\n"
        f"📉 <b>Old Price:</b> ₹{old_price:.2f}\n"
        f"📈 <b>New Price:</b> <b>₹{new_price:.2f}</b>\n\n"
        "<i>This new price is now immediately live in the bot!</i>",
        reply_markup=back_kb,
        parse_mode="HTML"
    )

# 2. Delete Package Flow
@dp.callback_query(F.data == "adm_del_pkg")
async def cb_adm_del_pkg(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    cats = db.get_categories()
    text = "🗑️ <b>DELETE PACKAGE</b>\n\nSelect Category to locate package:"
    await call.message.edit_text(text, reply_markup=kb.get_admin_categories_keyboard(cats, "adm_cat_del"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("adm_cat_del_"))
async def cb_adm_cat_del(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    cat_id = int(call.data.replace("adm_cat_del_", ""))
    brands = db.get_brands_by_category(cat_id)
    text = "🗑️ <b>DELETE PACKAGE</b>\n\nSelect Brand:"
    await call.message.edit_text(text, reply_markup=kb.get_admin_brands_keyboard(brands, cat_id, "adm_br_del"), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("adm_br_del_"))
async def cb_adm_br_del(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    brand_id = int(call.data.replace("adm_br_del_", ""))
    brand = db.get_brand(brand_id)
    pkgs = db.get_packages_by_brand(brand_id)
    bname = brand["name"] if brand else "Brand"
    text = f"🗑️ <b>DELETE PACKAGE FROM: {bname}</b>\n\nClick a package to permanently remove it:"
    await call.message.edit_text(text, reply_markup=kb.get_admin_del_packages_keyboard(pkgs, brand_id), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("adm_delpkg_conf_"))
async def cb_adm_delpkg_conf(call: types.CallbackQuery):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    pkg_id = int(call.data.replace("adm_delpkg_conf_", ""))
    pkg = db.get_package(pkg_id)
    dur = pkg.get("duration_label") or f"{pkg['duration_days']} Days" if pkg else "Package"
    bname = pkg["brand_name"] if pkg else ""
    db.delete_package(pkg_id)

    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🗑️ Delete Another", callback_data="adm_del_pkg")],
        [types.InlineKeyboardButton(text="👑 Back to Admin", callback_data="menu_admin_home")]
    ])
    await call.message.edit_text(
        f"🗑️ <b>Package Deleted!</b>\n\nSuccessfully removed <b>{bname} ({dur})</b> from store.",
        reply_markup=back_kb,
        parse_mode="HTML"
    )
    await call.answer("Package Deleted!", show_alert=True)

# 3. Interactive Send Key Prompt from Admin Menu
@dp.callback_query(F.data == "adm_sendkey_prompt")
async def cb_adm_sendkey_prompt(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id not in config.ADMIN_IDS:
        return
    await state.set_state(BotStates.admin_sending_key_userid)
    cancel_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_admin_home")]
    ])
    await call.message.answer(
        "🔑 <b>MANUAL KEY DELIVERY</b>\n\n"
        "Send the <b>User ID</b> of the buyer (or use <code>/sendkey &lt;user_id&gt; &lt;key&gt;</code> directly):",
        reply_markup=cancel_kb,
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(BotStates.admin_sending_key_userid)
async def process_adm_key_userid(message: types.Message, state: FSMContext):
    try:
        target_uid = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Invalid User ID! Please send a numeric User ID:")
        return

    await state.update_data(target_uid=target_uid)
    await state.set_state(BotStates.admin_sending_key_text)
    await message.answer(f"📝 Now send the <b>License Key</b> to deliver to <code>{target_uid}</code>:", parse_mode="HTML")

@dp.message(BotStates.admin_sending_key_text)
async def process_adm_key_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target_uid = data["target_uid"]
    key_str = message.text.strip()
    await state.clear()

    order_info = db.deliver_manual_key(target_uid, key_str)
    pkg = order_info.get("pkg")
    pkg_str = f"{pkg['brand_name']} ({format_duration(pkg['duration_days'])})" if pkg else "VIP Panel License"

    buyer_text = (
        "🎉 <b>PAYMENT APPROVED & LICENSE DELIVERED!</b> 🎉\n\n"
        f"📦 <b>Package:</b> {pkg_str}\n"
        f"🆔 <b>Order Ref:</b> <code>{order_info['order_ref']}</code>\n\n"
        f"🔑 <b>YOUR LICENSE KEY:</b>\n"
        f"<code>{key_str}</code>\n"
        "<i>(Tap to copy)</i>\n\n"
        f"⬇️ <b>Download Channel:</b> {config.DOWNLOAD_CHANNEL_URL}\n"
        f"🌐 <b>Support:</b> {config.SUPPORT_LINK}\n\n"
        "✨ <i>Thank you for purchasing! Key is also saved in your All History menu.</i>"
    )

    try:
        await bot.send_message(chat_id=target_uid, text=buyer_text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Failed to deliver key to {target_uid}: {e}")

    await message.answer(
        f"✅ <b>Key Successfully Delivered!</b>\n\n"
        f"👤 <b>Buyer:</b> <code>{target_uid}</code>\n"
        f"📦 <b>Package:</b> {pkg_str}\n"
        f"🔑 <b>Key:</b> <code>{key_str}</code>\n"
        f"🔖 <b>Order Ref:</b> <code>{order_info['order_ref']}</code>",
        parse_mode="HTML"
    )

# ==========================================
# 🚀 MAIN ENTRYPOINT
# ==========================================

async def main():
    logger.info("Initializing Database...")
    db.init_db()
    logger.info("Starting Bot Polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
