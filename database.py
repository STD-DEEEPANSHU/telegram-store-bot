import sqlite3
import datetime
from config import DB_PATH, REFERRAL_PERCENT

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        wallet_balance REAL DEFAULT 0.0,
        total_spent REAL DEFAULT 0.0,
        orders_completed INTEGER DEFAULT 0,
        referrer_id INTEGER DEFAULT NULL,
        total_referrals INTEGER DEFAULT 0,
        total_commission REAL DEFAULT 0.0,
        rank TEXT DEFAULT 'Regular User',
        joined_date TEXT,
        last_dice_claim TEXT DEFAULT NULL
    )
    """)

    # Categories (OS / Platform)
    c.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        icon TEXT
    )
    """)

    # Brands (under category)
    c.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT,
        icon TEXT,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
    """)

    # Packages (under brand)
    c.execute("""
    CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER,
        duration_days INTEGER,
        price_inr REAL,
        hwid_device INTEGER DEFAULT 1,
        download_link TEXT DEFAULT '',
        FOREIGN KEY (brand_id) REFERENCES brands (id)
    )
    """)

    # License Keys / Stock
    c.execute("""
    CREATE TABLE IF NOT EXISTS keys_stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_id INTEGER,
        license_key TEXT,
        is_used INTEGER DEFAULT 0,
        used_by INTEGER DEFAULT NULL,
        used_date TEXT DEFAULT NULL,
        FOREIGN KEY (package_id) REFERENCES packages (id)
    )
    """)

    # Orders Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_ref TEXT UNIQUE,
        user_id INTEGER,
        package_id INTEGER,
        amount_inr REAL,
        license_key TEXT,
        status TEXT,
        payment_method TEXT,
        created_at TEXT
    )
    """)

    # Promo Codes
    c.execute("""
    CREATE TABLE IF NOT EXISTS promo_codes (
        code TEXT PRIMARY KEY,
        reward_amount REAL,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)

    # Promo Claims
    c.execute("""
    CREATE TABLE IF NOT EXISTS promo_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        user_id INTEGER,
        claimed_at TEXT
    )
    """)

    # Manual Deposit Requests (Binance / bKash / Paytm)
    c.execute("""
    CREATE TABLE IF NOT EXISTS deposit_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        method TEXT,
        amount_inr REAL,
        order_ref TEXT,
        file_id TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TEXT
    )
    """)

    # Direct Order Requests (Direct Checkout via UPI QR)
    c.execute("""
    CREATE TABLE IF NOT EXISTS direct_order_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        package_id INTEGER,
        amount_inr REAL,
        order_ref TEXT,
        file_id TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TEXT
    )
    """)

    # Dynamic Bot Settings (Key-Value: texts, links, upi, etc.)
    c.execute("""
    CREATE TABLE IF NOT EXISTS bot_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT
    )
    """)

    # Dynamic Custom Buttons (Main menu buttons)
    c.execute("""
    CREATE TABLE IF NOT EXISTS custom_buttons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        button_text TEXT NOT NULL,
        button_type TEXT NOT NULL,
        button_value TEXT NOT NULL,
        row_position INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1
    )
    """)

    # Dynamic Custom Commands (/rules, /help, /apk, etc.)
    c.execute("""
    CREATE TABLE IF NOT EXISTS custom_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command TEXT UNIQUE NOT NULL,
        response_text TEXT NOT NULL,
        description TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()

    # Seed initial categories and packages if empty
    seed_default_data()
    # Seed default dynamic settings if empty
    seed_default_settings()

def get_or_create_user(user_id, username, full_name, referrer_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not row:
        valid_ref = None
        if referrer_id and referrer_id != user_id:
            c.execute("SELECT user_id FROM users WHERE user_id = ?", (referrer_id,))
            if c.fetchone():
                valid_ref = referrer_id
                c.execute("UPDATE users SET total_referrals = total_referrals + 1 WHERE user_id = ?", (referrer_id,))

        c.execute("""
            INSERT INTO users (user_id, username, full_name, wallet_balance, total_spent, orders_completed, referrer_id, joined_date)
            VALUES (?, ?, ?, 0.0, 0.0, 0, ?, ?)
        """, (user_id, username, full_name, valid_ref, now_str))
        conn.commit()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
    conn.close()
    return dict(row)

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_balance(user_id, amount_change):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id = ?", (amount_change, user_id))
    conn.commit()
    conn.close()

def get_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_brands_by_category(category_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM brands WHERE category_id = ? ORDER BY id ASC", (category_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_brand(brand_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM brands WHERE id = ?", (brand_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_packages_by_brand(brand_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM packages WHERE brand_id = ? ORDER BY duration_days ASC", (brand_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_package(package_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.*, b.name as brand_name, b.icon as brand_icon, c.name as category_name
        FROM packages p
        JOIN brands b ON p.brand_id = b.id
        JOIN categories c ON b.category_id = c.id
        WHERE p.id = ?
    """, (package_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_stock_count(package_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM keys_stock WHERE package_id = ? AND is_used = 0", (package_id,))
    count = c.fetchone()["cnt"]
    conn.close()
    return count

def pop_license_key(package_id, user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, license_key FROM keys_stock WHERE package_id = ? AND is_used = 0 LIMIT 1", (package_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
    key_id = row["id"]
    key_val = row["license_key"]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("UPDATE keys_stock SET is_used = 1, used_by = ?, used_date = ? WHERE id = ?", (user_id, now_str, key_id))
    conn.commit()
    conn.close()
    return key_val

def add_keys_bulk(package_id, keys_list):
    conn = get_connection()
    c = conn.cursor()
    inserted = 0
    for k in keys_list:
        k = k.strip()
        if k:
            c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)", (package_id, k))
            inserted += 1
    conn.commit()
    conn.close()
    return inserted

def create_completed_order(order_ref, user_id, package_id, amount_inr, license_key, payment_method):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO orders (order_ref, user_id, package_id, amount_inr, license_key, status, payment_method, created_at)
        VALUES (?, ?, ?, ?, ?, 'COMPLETED', ?, ?)
    """, (order_ref, user_id, package_id, amount_inr, license_key, payment_method, now_str))

    # Update user stats
    c.execute("""
        UPDATE users 
        SET orders_completed = orders_completed + 1, total_spent = total_spent + ?
        WHERE user_id = ?
    """, (amount_inr, user_id))

    # Give referral commission if user was referred
    c.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    user_row = c.fetchone()
    if user_row and user_row["referrer_id"]:
        ref_id = user_row["referrer_id"]
        comm = (amount_inr * REFERRAL_PERCENT) / 100.0
        c.execute("""
            UPDATE users 
            SET wallet_balance = wallet_balance + ?, total_commission = total_commission + ?
            WHERE user_id = ?
        """, (comm, comm, ref_id))

    conn.commit()
    conn.close()

def get_user_orders(user_id, limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT o.*, p.duration_days, b.name as brand_name
        FROM orders o
        LEFT JOIN packages p ON o.package_id = p.id
        LEFT JOIN brands b ON p.brand_id = b.id
        WHERE o.user_id = ?
        ORDER BY o.id DESC LIMIT ?
    """, (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def claim_promo(user_id, code_input):
    conn = get_connection()
    c = conn.cursor()
    code = code_input.strip().upper()
    c.execute("SELECT * FROM promo_codes WHERE code = ?", (code,))
    promo = c.fetchone()
    if not promo:
        conn.close()
        return False, "❌ Invalid promo code! Please check and try again."
    
    if promo["used_count"] >= promo["max_uses"]:
        conn.close()
        return False, "❌ This promo code has reached its maximum claim limit!"

    c.execute("SELECT id FROM promo_claims WHERE code = ? AND user_id = ?", (code, user_id))
    if c.fetchone():
        conn.close()
        return False, "❌ You have already claimed this promo code!"

    reward = promo["reward_amount"]
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.execute("INSERT INTO promo_claims (code, user_id, claimed_at) VALUES (?, ?, ?)", (code, user_id, now_str))
    c.execute("UPDATE promo_codes SET used_count = used_count + 1 WHERE code = ?", (code,))
    c.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id = ?", (reward, user_id))
    conn.commit()
    conn.close()
    return True, f"🎉 Success! ₹{reward:.2f} has been added to your wallet balance."

def create_promo(code, reward_amount, max_uses):
    conn = get_connection()
    c = conn.cursor()
    code = code.strip().upper()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT OR REPLACE INTO promo_codes (code, reward_amount, max_uses, used_count, created_at)
        VALUES (?, ?, ?, 0, ?)
    """, (code, reward_amount, max_uses, now_str))
    conn.commit()
    conn.close()

def can_claim_ludo(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_dice_claim FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row or not row["last_dice_claim"]:
        return True, 0
    
    last = datetime.datetime.strptime(row["last_dice_claim"], "%Y-%m-%d %H:%M:%S")
    diff = datetime.datetime.now() - last
    if diff.total_seconds() >= 86400:  # 24 hours
        return True, 0
    else:
        remaining_hours = int((86400 - diff.total_seconds()) // 3600)
        remaining_minutes = int(((86400 - diff.total_seconds()) % 3600) // 60)
        return False, f"{remaining_hours}h {remaining_minutes}m"

def record_ludo_claim(user_id, reward_amount):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        UPDATE users 
        SET wallet_balance = wallet_balance + ?, last_dice_claim = ?
        WHERE user_id = ?
    """, (reward_amount, now_str, user_id))
    conn.commit()
    conn.close()

def record_deposit_request(user_id, method, amount_inr, order_ref, file_id):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO deposit_requests (user_id, method, amount_inr, order_ref, file_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
    """, (user_id, method, amount_inr, order_ref, file_id, now_str))
    req_id = c.lastrowid
    conn.commit()
    conn.close()
    return req_id

def approve_deposit(req_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM deposit_requests WHERE id = ? AND status = 'PENDING'", (req_id,))
    req = c.fetchone()
    if not req:
        conn.close()
        return None
    c.execute("UPDATE deposit_requests SET status = 'APPROVED' WHERE id = ?", (req_id,))
    c.execute("UPDATE users SET wallet_balance = wallet_balance + ? WHERE user_id = ?", (req["amount_inr"], req["user_id"]))
    conn.commit()
    conn.close()
    return dict(req)

def reject_deposit(req_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM deposit_requests WHERE id = ? AND status = 'PENDING'", (req_id,))
    req = c.fetchone()
    if not req:
        conn.close()
        return None
    c.execute("UPDATE deposit_requests SET status = 'REJECTED' WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    return dict(req)

def record_direct_order_request(user_id, package_id, amount_inr, order_ref, file_id):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
        INSERT INTO direct_order_requests (user_id, package_id, amount_inr, order_ref, file_id, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'PENDING', ?)
    """, (user_id, package_id, amount_inr, order_ref, file_id, now_str))
    req_id = c.lastrowid
    conn.commit()
    conn.close()
    return req_id

def approve_direct_order(order_req_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM direct_order_requests WHERE id = ? AND status = 'PENDING'", (order_req_id,))
    req = c.fetchone()
    if not req:
        conn.close()
        return None, None, None

    user_id = req["user_id"]
    pkg_id = req["package_id"]
    price = req["amount_inr"]
    order_ref = req["order_ref"]

    key = pop_license_key(pkg_id, user_id)
    if not key:
        conn.close()
        return dict(req), None, "OUT_OF_STOCK"

    c.execute("UPDATE direct_order_requests SET status = 'APPROVED' WHERE id = ?", (order_req_id,))
    conn.commit()
    conn.close()

    create_completed_order(order_ref, user_id, pkg_id, price, key, "DIRECT_UPI_QR")
    pkg = get_package(pkg_id)
    return dict(req), key, pkg

def reject_direct_order(order_req_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM direct_order_requests WHERE id = ? AND status = 'PENDING'", (order_req_id,))
    req = c.fetchone()
    if not req:
        conn.close()
        return None
    c.execute("UPDATE direct_order_requests SET status = 'REJECTED' WHERE id = ?", (order_req_id,))
    conn.commit()
    conn.close()
    return dict(req)

def deliver_manual_key(user_id: int, key: str, req_id: int = None):
    conn = get_connection()
    c = conn.cursor()
    req = None
    if req_id:
        c.execute("SELECT * FROM direct_order_requests WHERE id = ?", (req_id,))
        req = c.fetchone()
    else:
        c.execute("SELECT * FROM direct_order_requests WHERE user_id = ? AND status = 'PENDING' ORDER BY id DESC LIMIT 1", (user_id,))
        req = c.fetchone()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if req:
        order_ref = req["order_ref"]
        pkg_id = req["package_id"]
        amount = req["amount_inr"]
        c.execute("UPDATE direct_order_requests SET status = 'APPROVED' WHERE id = ?", (req["id"],))
    else:
        order_ref = f"MAN{user_id}T{int(time.time())}"
        pkg_id = None
        amount = 0.0

    c.execute("""
        INSERT INTO orders (order_ref, user_id, package_id, amount_inr, license_key, status, payment_method, created_at)
        VALUES (?, ?, ?, ?, ?, 'COMPLETED', 'ADMIN_MANUAL', ?)
    """, (order_ref, user_id, pkg_id, amount, key, now_str))

    conn.commit()
    conn.close()

    pkg = get_package(pkg_id) if pkg_id else None
    return {
        "order_ref": order_ref,
        "user_id": user_id,
        "amount_inr": amount,
        "license_key": key,
        "pkg": pkg
    }

def update_package_price(package_id: int, new_price: float):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE packages SET price_inr = ? WHERE id = ?", (new_price, package_id))
    conn.commit()
    conn.close()
    return True

def delete_package(package_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM keys_stock WHERE package_id = ?", (package_id,))
    c.execute("DELETE FROM packages WHERE id = ?", (package_id,))
    conn.commit()
    conn.close()
    return True

def get_stats():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total_users, SUM(wallet_balance) as total_balance FROM users")
    u_stats = c.fetchone()
    c.execute("SELECT COUNT(*) as total_orders, SUM(amount_inr) as total_revenue FROM orders WHERE status = 'COMPLETED'")
    o_stats = c.fetchone()
    c.execute("SELECT COUNT(*) as available_keys FROM keys_stock WHERE is_used = 0")
    k_stats = c.fetchone()
    conn.close()
    return {
        "users": u_stats["total_users"] or 0,
        "balance": u_stats["total_balance"] or 0.0,
        "orders": o_stats["total_orders"] or 0,
        "revenue": o_stats["total_revenue"] or 0.0,
        "stock": k_stats["available_keys"] or 0
    }

def seed_default_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM categories")
    if c.fetchone()["cnt"] > 0:
        conn.close()
        return

    # Categories
    cats = [
        ("🤖 ANDROID NON ROOT PANEL", "🤖"),
        ("🤖 ANDROID ROOT PANEL", "🤖"),
        ("🍏 IPHONE PANEL", "🍏"),
        ("💻 PC PANEL", "💻")
    ]
    for name, icon in cats:
        c.execute("INSERT INTO categories (name, icon) VALUES (?, ?)", (name, icon))

    # PC Panel Brands & Packages
    c.execute("SELECT id FROM categories WHERE name = '💻 PC PANEL'")
    pc_cat_id = c.fetchone()["id"]
    c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, 'BR_MODS PC ! + BYPASS', '🛒')", (pc_cat_id,))
    br_mods_id = c.lastrowid
    pc_packages = [
        (br_mods_id, 1, 120.0, 1),
        (br_mods_id, 10, 499.0, 1),
        (br_mods_id, 30, 999.0, 1)
    ]
    c.executemany("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, ?)", pc_packages)

    # iPhone Panel Brands & Packages
    c.execute("SELECT id FROM categories WHERE name = '🍏 IPHONE PANEL'")
    ios_cat_id = c.fetchone()["id"]

    # 1. AIMHACK iOS
    c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, 'AIMHACK iOS', '🍏')", (ios_cat_id,))
    aim_id = c.lastrowid
    aim_packages = [
        (aim_id, 3, 400.0, 1),
        (aim_id, 7, 899.0, 1),
        (aim_id, 30, 1399.0, 1)
    ]
    c.executemany("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, ?)", aim_packages)

    # 2. TROLL iOS
    c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, 'TROLL iOS', '🍏')", (ios_cat_id,))
    troll_id = c.lastrowid
    troll_packages = [
        (troll_id, 3, 250.0, 1),
        (troll_id, 7, 450.0, 1),
        (troll_id, 15, 699.0, 1),
        (troll_id, 30, 999.0, 1)
    ]
    c.executemany("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, ?)", troll_packages)

    # 3. ALPHA REGEDIT EXTERNAL
    c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, 'ALPHA REGEDIT EXTERNAL', '🍏')", (ios_cat_id,))
    alpha_id = c.lastrowid
    alpha_packages = [
        (alpha_id, 1, 120.0, 1),
        (alpha_id, 3, 200.0, 1),
        (alpha_id, 7, 350.0, 1),
        (alpha_id, 30, 999.0, 1)
    ]
    c.executemany("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, ?)", alpha_packages)

    # Add some demo keys to test right away
    c.execute("SELECT id FROM packages")
    pkg_ids = [r["id"] for r in c.fetchall()]
    for pid in pkg_ids:
        # Add 3 test stock keys for each package
        for i in range(1, 4):
            key = f"PANEL-KEY-{pid}-{i}X9Z"
            c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)", (pid, key))

    # Add a default Promo code: WELCOME50 (₹50 bonus)
    c.execute("""
        INSERT INTO promo_codes (code, reward_amount, max_uses, used_count, created_at)
        VALUES ('WELCOME50', 50.0, 1000, 0, datetime('now'))
    """)

    conn.commit()
    conn.close()

def seed_default_settings():
    conn = get_connection()
    c = conn.cursor()
    default_settings = [
        ("store_name", "FF PANEL STORE", "Display name of the store"),
        ("store_tagline", "Official Gaming Panels & Instant Key Delivery", "Store tagline"),
        ("welcome_msg", (
            "⚡ <b>{store_name}</b> ⚡\n"
            "<i>{store_tagline}</i>\n\n"
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
        ), "Main welcome text for /start"),
        ("support_link", "https://t.me/kartik_owner", "Telegram support link or username"),
        ("download_channel_url", "https://t.me/kartik_channel", "Download channel URL"),
        ("music_app_url", "https://stdmusicapp-f82ba5b47ed8.herokuapp.com/static/STD_MUSIC.apk", "Music App download URL"),
        ("tutorial_video_url", "https://youtu.be/dQw4w9WgXcQ", "Tutorial video URL"),
        ("paytm_upi_id", "8449767748@ptaxis", "Paytm UPI ID for direct checkout"),
        ("payee_name", "STD Store", "Payee display name on UPI QR")
    ]

    for key, val, desc in default_settings:
        c.execute("INSERT OR IGNORE INTO bot_settings (key, value, description) VALUES (?, ?, ?)", (key, val, desc))

    # Add default /rules command if not existing
    c.execute("SELECT COUNT(*) as cnt FROM custom_commands WHERE command = 'rules'")
    if c.fetchone()["cnt"] == 0:
        c.execute("""
            INSERT INTO custom_commands (command, response_text, description)
            VALUES (?, ?, ?)
        """, (
            "rules",
            "📜 <b>STORE RULES & POLICY</b>\n\n1. Do not share your license key with multiple unauthorized devices.\n2. All delivered keys are tested and verified before delivery.\n3. For any billing or key issues, contact our support team.",
            "Store rules and policy"
        ))

    conn.commit()
    conn.close()

# ==========================================
# ⚙️ BOT SETTINGS & CONFIGURATION
# ==========================================

def get_setting(key: str, default=None) -> str:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    if row and row["value"] is not None:
        return row["value"]
    return default

def set_setting(key: str, value: str, description: str = ""):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO bot_settings (key, value, description)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value, description))
    conn.commit()
    conn.close()

def get_all_settings() -> dict:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT key, value, description FROM bot_settings")
    rows = c.fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

# ==========================================
# 🔘 DYNAMIC CUSTOM BUTTONS
# ==========================================

def get_custom_buttons(active_only=True) -> list:
    conn = get_connection()
    c = conn.cursor()
    if active_only:
        c.execute("SELECT * FROM custom_buttons WHERE is_active = 1 ORDER BY row_position ASC, id ASC")
    else:
        c.execute("SELECT * FROM custom_buttons ORDER BY row_position ASC, id ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_custom_button(button_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM custom_buttons WHERE id = ?", (button_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def add_custom_button(button_text: str, button_type: str, button_value: str, row_position: int = 1) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO custom_buttons (button_text, button_type, button_value, row_position, is_active)
        VALUES (?, ?, ?, ?, 1)
    """, (button_text, button_type, button_value, row_position))
    btn_id = c.lastrowid
    conn.commit()
    conn.close()
    return btn_id

def delete_custom_button(button_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM custom_buttons WHERE id = ?", (button_id,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes > 0

# ==========================================
# ⚡ DYNAMIC CUSTOM COMMANDS
# ==========================================

def get_custom_commands() -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM custom_commands ORDER BY command ASC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_custom_command(cmd_name: str):
    cmd_clean = cmd_name.strip().lstrip("/").lower()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM custom_commands WHERE LOWER(command) = ?", (cmd_clean,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def set_custom_command(cmd_name: str, response_text: str, description: str = ""):
    cmd_clean = cmd_name.strip().lstrip("/").lower()
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO custom_commands (command, response_text, description)
        VALUES (?, ?, ?)
        ON CONFLICT(command) DO UPDATE SET response_text = excluded.response_text
    """, (cmd_clean, response_text, description))
    conn.commit()
    conn.close()

def delete_custom_command(cmd_name: str) -> bool:
    cmd_clean = cmd_name.strip().lstrip("/").lower()
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM custom_commands WHERE LOWER(command) = ?", (cmd_clean,))
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes > 0

# ==========================================
# 🏷️ BRAND & PACKAGE CREATION / DELETION
# ==========================================

def add_brand(category_id: int, name: str, icon: str = "🛒") -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, ?, ?)", (category_id, name, icon))
    bid = c.lastrowid
    conn.commit()
    conn.close()
    return bid

def delete_brand(brand_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM packages WHERE brand_id = ?", (brand_id,))
    c.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
    conn.commit()
    conn.close()
    return True

def add_package(brand_id: int, duration_days: float, price_inr: float, duration_label: str = None, hwid_device: int = 1) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO packages (brand_id, duration_days, duration_label, price_inr, hwid_device)
        VALUES (?, ?, ?, ?, ?)
    """, (brand_id, duration_days, duration_label, price_inr, hwid_device))
    pkg_id = c.lastrowid
    conn.commit()
    conn.close()
    return pkg_id
