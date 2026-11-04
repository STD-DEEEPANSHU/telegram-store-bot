from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME, DOWNLOAD_CHANNEL_URL, TUTORIAL_VIDEO_URL, INR_TO_USD_RATE
import database as db

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    support_raw = db.get_setting("support_link", SUPPORT_USERNAME)
    support_url = support_raw if support_raw.startswith("http") else f"https://t.me/{support_raw.replace('@', '')}"
    music_url = db.get_setting("music_app_url", "https://stdmusicapp-f82ba5b47ed8.herokuapp.com/static/STD_MUSIC.apk")
    
    keyboard = [
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
            InlineKeyboardButton(text="🎵 STD Music App ↗️", url=music_url),
            InlineKeyboardButton(text="⬇️ Download Files", callback_data="menu_downloads")
        ]
    ]

    # Dynamically append admin-configured custom buttons
    custom_btns = db.get_custom_buttons(active_only=True)
    if custom_btns:
        for btn in custom_btns:
            if btn["button_type"] == "url":
                b_text = btn["button_text"] if "↗" in btn["button_text"] else f"{btn['button_text']} ↗️"
                keyboard.append([InlineKeyboardButton(text=b_text, url=btn["button_value"])])
            else:
                keyboard.append([InlineKeyboardButton(text=btn["button_text"], callback_data=f"cbtn_{btn['id']}")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

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
    tut_url = db.get_setting("tutorial_video_url", TUTORIAL_VIDEO_URL)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎬 Watch Full Video Tutorial ↗️", url=tut_url)],
        [InlineKeyboardButton(text="🔙 BACK", callback_data="menu_home")]
    ])

def get_downloads_keyboard() -> InlineKeyboardMarkup:
    dl_url = db.get_setting("download_channel_url", DOWNLOAD_CHANNEL_URL)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬇️ Access Download Channel ↗️", url=dl_url)],
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
            InlineKeyboardButton(text="💰 Change Price", callback_data="adm_change_price"),
            InlineKeyboardButton(text="📦 Products & Brands", callback_data="adm_manage_catalog")
        ],
        [
            InlineKeyboardButton(text="🔘 Custom Buttons", callback_data="adm_manage_buttons"),
            InlineKeyboardButton(text="⚡ Custom Commands", callback_data="adm_manage_commands")
        ],
        [
            InlineKeyboardButton(text="📝 Edit Texts & Links", callback_data="adm_manage_texts"),
            InlineKeyboardButton(text="🔑 Send Key (/sendkey)", callback_data="adm_sendkey_prompt")
        ],
        [
            InlineKeyboardButton(text="💳 Credit User Balance", callback_data="adm_add_bal"),
            InlineKeyboardButton(text="🎟️ Create Promo Code", callback_data="adm_create_promo")
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast Message", callback_data="adm_broadcast"),
            InlineKeyboardButton(text="📦 Add Stock Keys", callback_data="adm_add_keys")
        ],
        [
            InlineKeyboardButton(text="📊 Bot Analytics", callback_data="adm_stats"),
            InlineKeyboardButton(text="🔙 Exit Admin", callback_data="menu_home")
        ]
    ])

def get_admin_texts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Welcome Message (/start)", callback_data="adm_edit_txt_welcome_msg")],
        [
            InlineKeyboardButton(text="🌐 Support Link", callback_data="adm_edit_txt_support_link"),
            InlineKeyboardButton(text="⬇️ Download Channel", callback_data="adm_edit_txt_download_channel_url")
        ],
        [
            InlineKeyboardButton(text="🎵 Music App APK Link", callback_data="adm_edit_txt_music_app_url"),
            InlineKeyboardButton(text="🎬 Tutorial Video Link", callback_data="adm_edit_txt_tutorial_video_url")
        ],
        [
            InlineKeyboardButton(text="📲 Paytm UPI ID", callback_data="adm_edit_txt_paytm_upi_id"),
            InlineKeyboardButton(text="🏷️ Payee Name", callback_data="adm_edit_txt_payee_name")
        ],
        [InlineKeyboardButton(text="🏪 Store Name & Tagline", callback_data="adm_edit_txt_store_name")],
        [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin_home")]
    ])

def get_admin_buttons_keyboard(buttons: list) -> InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([InlineKeyboardButton(text="➕ Add New Custom Button", callback_data="adm_add_cbtn_start")])
    for btn in buttons:
        b_type = "🔗 URL" if btn["button_type"] == "url" else "💬 Text"
        keyboard.append([
            InlineKeyboardButton(text=f"{btn['button_text']} ({b_type})", callback_data=f"adm_view_cbtn_{btn['id']}"),
            InlineKeyboardButton(text="🗑️ Delete", callback_data=f"adm_del_cbtn_{btn['id']}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin_home")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_commands_keyboard(commands: list) -> InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([InlineKeyboardButton(text="➕ Add New Command", callback_data="adm_add_ccmd_start")])
    for cmd in commands:
        keyboard.append([
            InlineKeyboardButton(text=f"/{cmd['command']}", callback_data=f"adm_view_ccmd_{cmd['command']}"),
            InlineKeyboardButton(text="🗑️ Delete", callback_data=f"adm_del_ccmd_{cmd['command']}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin_home")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_catalog_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Add New Package", callback_data="adm_add_pkg_cat"),
            InlineKeyboardButton(text="🗑️ Delete Package", callback_data="adm_del_pkg")
        ],
        [
            InlineKeyboardButton(text="🏷️ Add New Brand", callback_data="adm_add_br_cat"),
            InlineKeyboardButton(text="🗑️ Delete Brand", callback_data="adm_del_br_cat")
        ],
        [InlineKeyboardButton(text="🔙 Back to Admin", callback_data="menu_admin_home")]
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
    if action_prefix == "adm_br_price":
        back_target = "adm_change_price"
    elif action_prefix == "adm_br_stock":
        back_target = "adm_add_keys"
    else:
        back_target = "adm_del_pkg"
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

def get_admin_stock_packages_keyboard(packages: list, brand_id: int) -> InlineKeyboardMarkup:
    keyboard = []
    for pkg in packages:
        dur = pkg.get("duration_label") or f"{pkg['duration_days']} Days"
        stock = db.get_stock_count(pkg["id"])
        text = f"📦 {dur} (Stock: {stock})"
        keyboard.append([InlineKeyboardButton(text=text, callback_data=f"adm_sel_pkg_stock_{pkg['id']}")])
    brand = db.get_brand(brand_id)
    cat_id = brand["category_id"] if brand else 1
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Brands", callback_data=f"adm_cat_stock_{cat_id}")])
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
