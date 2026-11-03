import sqlite3
import os

db_path = r"C:\Users\STD DEEPANSHU\.gemini\antigravity\scratch\kartik_store_bot\store.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT id FROM categories WHERE name = '🤖 ANDROID ROOT PANEL'")
row = c.fetchone()
if not row:
    c.execute("INSERT INTO categories (name, icon) VALUES ('🤖 ANDROID ROOT PANEL', '🤖')")
    root_cat_id = c.lastrowid
else:
    root_cat_id = row["id"]

android_root_brands = [
    ("Zytron Pro Apk", "🌌"),
    ("Angry Mod Apk", "👿"),
    ("Xreg Safe Apk", "🌌"),
    ("Hikari Mod Apk", "🌊"),
    ("Lk Team Apk", "🛡️"),
    ("Br Mods Apk", "🆑"),
    ("RAPID CORE ROOT", "🚀"),
    ("XYZ CHEATS ROOT", "🛒"),
    ("HEX BLADE ROOT APK", "🥷"),
    ("ROCKET MODS ROOT APK", "🚀"),
    ("ZREX ROOT APK", "⚡"),
    ("DRIP CLIENT ROOT", "😈"),
    ("INVISIBLE X EXTERNAL", "🛡️"),
    ("HAXX-CKER PRO", "💀"),
    ("ST MOD ROOT", "🎯"),
    ("SILENT CHEATS ROOT", "🌌")
]

for bname, bicon in android_root_brands:
    c.execute("SELECT id FROM brands WHERE category_id = ? AND name = ?", (root_cat_id, bname))
    exist = c.fetchone()
    if not exist:
        c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, ?, ?)", (root_cat_id, bname, bicon))
        b_id = c.lastrowid
    else:
        b_id = exist["id"]

    # If ZREX ROOT APK, add exact prices: 1 Day ₹70, 3 Days ₹120, 7 Days ₹180
    c.execute("SELECT COUNT(*) as cnt FROM packages WHERE brand_id = ?", (b_id,))
    if c.fetchone()["cnt"] == 0:
        if "ZREX" in bname:
            pkgs = [(b_id, 1, 70.0, 1), (b_id, 3, 120.0, 1), (b_id, 7, 180.0, 1)]
        else:
            pkgs = [(b_id, 1, 80.0, 1), (b_id, 3, 150.0, 1), (b_id, 7, 250.0, 1), (b_id, 30, 600.0, 1)]
        c.executemany("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, ?)", pkgs)

# Add keys for all packages that have 0 stock
c.execute("SELECT id FROM packages")
all_pkgs = c.fetchall()
for p in all_pkgs:
    pid = p["id"]
    c.execute("SELECT COUNT(*) as cnt FROM keys_stock WHERE package_id = ? AND is_used = 0", (pid,))
    if c.fetchone()["cnt"] == 0:
        for i in range(1, 4):
            key = f"ROOT-KEY-{pid}-{i}X9A"
            c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)", (pid, key))

conn.commit()
conn.close()
print("Android Root brands, packages and stock keys successfully added!")
