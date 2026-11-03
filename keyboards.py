from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME, DOWNLOAD_CHANNEL_URL, TUTORIAL_VIDEO_URL, INR_TO_USD_RATE
import database as db

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    support_url = SUPPORT_USERNAME if SUPPORT_USERNAME.startswith("http") else f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Product Store", callback_data="menu_store")],
        [
            InlineKeyboardButton(text="👤 My Profile", callback_data="menu_profile"),
            InlineKeyboardButton(text="💰 Add Balance", callback_data="menu_deposit")
        ],
        [
            InlineKeyboardButton(text="🔑 All History", callback_data="menu_history"),
            InlineKeyboardButton(text="👥 Referral", callback_data="menu_referral")
        ],
        [
            InlineKeyboardButton(text="🎬 Tutorials", callback_data="menu_tutorials"),
            InlineKeyboardButton(text="🌐 Support", url=support_url)
        ],
        [
            InlineKeyboardButton(text="🎵 STD Music App ↗️", url="https://stdmusicapp-f82ba5b47ed8.herokuapp.com/static/STD_MUSIC.apk"),
            InlineKeyboardButton(text="⬇️ Download Files", callback_data="menu_downloads")
        ]
    ])

def get_profile_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎟️ Redeem Promo Code", callback_data="redeem_promo")],
        [InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

def get_referral_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

def get_tutorials_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Watch Full Video Tutorial ↗️", url=TUTORIAL_VIDEO_URL)],
        [InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

def get_downloads_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ Access Download Channel ↗️", url=DOWNLOAD_CHANNEL_URL)],
        [InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

def get_categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(text=cat["name"], callback_data=f"cat_{cat['id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_brands_keyboard(brands: list, category_id: int) -> InlineKeyboardMarkup:
    keyboard = []
    for brand in brands:
        icon = brand.get("icon") or "🛒"
        keyboard.append([InlineKeyboardButton(text=f"{icon} {brand['name']}", callback_data=f"brand_{brand['id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 BACK TO PANELS", callback_data="menu_store")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_packages_keyboard(packages: list, brand_id: int) -> InlineKeyboardMarkup:
    keyboard = []
    for pkg in packages:
        stock = db.get_stock_count(pkg["id"])
        usd_price = pkg["price_inr"] * INR_TO_USD_RATE
        if pkg.get("duration_label"):
            dur_str = pkg["duration_label"]
        else:
            try:
                dur_val = float(pkg["duration_days"])
                if dur_val == 0.25:
                    dur_str = "6 Hours"
                elif dur_val < 1.0 or dur_val in (0.0, 0.5):
                    dur_str = "12 Hours"
                else:
                    dur_str = f"{int(dur_val)} Days"
            except (ValueError, TypeError):
                dur_str = f"{pkg['duration_days']} Days"
        if stock > 0:
            text = f"🛒 Buy {dur_str} - ₹{pkg['price_inr']:.2f} (~ ${usd_price:.2f})"
            callback = f"buy_{pkg['id']}"
        else:
            text = f"❌ {dur_str} (Out of Stock)"
            callback = f"outofstock_{pkg['id']}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=callback)])
    
    brand = db.get_brand(brand_id)
    cat_id = brand["category_id"] if brand else 1
    keyboard.append([InlineKeyboardButton(text="🔙 BACK TO PANELS", callback_data=f"cat_{cat_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_deposit_methods_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📲 Paytm UPI", callback_data="dep_paytm"),
            InlineKeyboardButton(text="🪙 Binance Pay", callback_data="dep_binance")
        ],
        [InlineKeyboardButton(text="🇧🇩 bKash (taka)", callback_data="dep_bkash")],
        [InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

def get_paytm_amounts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="₹50", callback_data="paytm_amt_50"),
            InlineKeyboardButton(text="₹100", callback_data="paytm_amt_100")
        ],
        [
            InlineKeyboardButton(text="₹200", callback_data="paytm_amt_200"),
            InlineKeyboardButton(text="₹500", callback_data="paytm_amt_500")
        ],
        [InlineKeyboardButton(text="✏️ Custom Amount", callback_data="paytm_amt_custom")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="menu_deposit")]
    ])

def get_cancel_deposit_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_deposit")]
    ])

def get_direct_checkout_keyboard(order_ref: str, package_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ I Have Paid (Confirm)", callback_data=f"confirm_pay_{order_ref}_{package_id}")],
        [InlineKeyboardButton(text="🔙 Cancel", callback_data="menu_store")]
    ])

def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💰 Change Package Price", callback_data="adm_change_price"),
            InlineKeyboardButton(text="🗑️ Delete Package", callback_data="adm_del_pkg")
        ],
        [
            InlineKeyboardButton(text="🔑 Send Key (/sendkey)", callback_data="adm_sendkey_prompt"),
            InlineKeyboardButton(text="💳 Credit User Balance", callback_data="adm_add_bal")
        ],
        [
            InlineKeyboardButton(text="🎟️ Create Promo Code", callback_data="adm_create_promo"),
            InlineKeyboardButton(text="📢 Broadcast Message", callback_data="adm_broadcast")
        ],
        [
            InlineKeyboardButton(text="📦 Add Stock Keys", callback_data="adm_add_keys"),
            InlineKeyboardButton(text="📊 Bot Analytics", callback_data="adm_stats")
        ],
        [InlineKeyboardButton(text="🔙 Exit Admin", callback_data="menu_home")]
    ])

def get_direct_order_action_keyboard(req_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔑 Send Key Now", callback_data=f"send_key_req_{req_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"rejc_ord_{req_id}")
        ]
    ])

def get_admin_categories_keyboard(categories: list, action_prefix: str = "adm_cat_price") -> InlineKeyboardMarkup:
    keyboard = []
    for cat in categories:
        keyboard.append([InlineKeyboardButton(text=cat["name"], callback_data=f"{action_prefix}_{cat['id']}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin_home")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_brands_keyboard(brands: list, cat_id: int, action_prefix: str = "adm_br_price") -> InlineKeyboardMarkup:
    keyboard = []
    for brand in brands:
        icon = brand.get("icon") or "🛒"
        keyboard.append([InlineKeyboardButton(text=f"{icon} {brand['name']}", callback_data=f"{action_prefix}_{brand['id']}")])
    back_target = "adm_change_price" if action_prefix == "adm_br_price" else "adm_del_pkg"
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Categories", callback_data=back_target)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_packages_keyboard(packages: list, brand_id: int) -> InlineKeyboardMarkup:
    keyboard = []
    for pkg in packages:
        dur = pkg.get("duration_label") or f"{pkg['duration_days']} Days"
        text = f"📦 {dur} - ₹{pkg['price_inr']:.2f}"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"adm_setprice_pkg_{pkg['id']}")])
    brand = db.get_brand(brand_id)
    cat_id = brand["category_id"] if brand else 1
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Brands", callback_data=f"adm_cat_price_{cat_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_del_packages_keyboard(packages: list, brand_id: int) -> InlineKeyboardMarkup:
    keyboard = []
    for pkg in packages:
        dur = pkg.get("duration_label") or f"{pkg['duration_days']} Days"
        text = f"🗑️ Delete {dur} (₹{pkg['price_inr']:.2f})"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"adm_delpkg_conf_{pkg['id']}")])
    brand = db.get_brand(brand_id)
    cat_id = brand["category_id"] if brand else 1
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Brands", callback_data=f"adm_cat_del_{cat_id}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_deposit_action_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"appr_dep_{deposit_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"rejc_dep_{deposit_id}")
        ]
    ])
