import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")

NON_ROOT_BRANDS = [
    {"name": "Ctb Mods Apk", "icon": "🟢"},
    {"name": "ABCD Panel", "icon": "🌌"},
    {"name": "NINE X MOD", "icon": "⚡"},
    {"name": "Hg Proxy Apk", "icon": "🌐"},
    {"name": "Patoteam Orange", "icon": "🟠"},
    {"name": "Patoteam Blue", "icon": "🔵"},
    {"name": "Br Mods Non Root", "icon": "🇧🇷"},
    {"name": "Drip Wire Extrnal Apk", "icon": "👾"},
    {"name": "SILENT CHEATS PROXY APK", "icon": "🔇"},
    {"name": "BALA MODS APK", "icon": "🎯"},
    {"name": "ZREX APK [NON ROOT]", "icon": "🦖"},
    {"name": "XYZ CHEATS [NON ROOT]", "icon": "🚀"},
    {"name": "TROLL MODZ APK", "icon": "🤡"},
    {"name": "HEX BLADE APK MOD", "icon": "⚔️"},
    {"name": "RAPID CORE APKMOD [NON ROOT]", "icon": "⚡"},
    {"name": "PRIME MODS APK", "icon": "👑"},
    {"name": "SILENT CHEATS APKMOD", "icon": "🤫"},
    {"name": "DRIP CLIENT APKMOD", "icon": "💧"},
    {"name": "DRIP CLIENT PROXY APK", "icon": "💎"},
    {"name": "HG CHEATS APK", "icon": "🛡️"},
    {"name": "Xreg ApkMod [NON ROOT]", "icon": "⚙️"},
    {"name": "PHANTOM [NON ROOT+ iOS]", "icon": "👻"},
    {"name": "RAPID CORE BOT NO ROOT", "icon": "🤖"},
    {"name": "MYTH PANEL", "icon": "🔮"}
]

def populate_non_root():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Category 1 = ANDROID NON ROOT PANEL
    c.execute("SELECT id FROM categories WHERE name LIKE '%NON ROOT%'")
    row = c.fetchone()
    if not row:
        c.execute("INSERT INTO categories (name, description, icon) VALUES (?, ?, ?)",
                  ("🛒 ANDROID NON ROOT PANEL", "Non-Root safe APK mods & panels", "🛒"))
        cat_id = c.lastrowid
    else:
        cat_id = row[0]

    for b in NON_ROOT_BRANDS:
        c.execute("SELECT id FROM brands WHERE name = ? AND category_id = ?", (b["name"], cat_id))
        b_row = c.fetchone()
        if not b_row:
            c.execute("INSERT INTO brands (category_id, name, icon) VALUES (?, ?, ?)",
                      (cat_id, b["name"], b["icon"]))
            brand_id = c.lastrowid
        else:
            brand_id = b_row[0]

        # Packages
        if b["name"] == "ZREX APK [NON ROOT]":
            pkgs = [
                (1, 60.0),
                (3, 100.0),
                (7, 170.0)
            ]
        elif b["name"] == "Hg Proxy Apk":
            pkgs = [
                (1, 90.0),
                (7, 250.0),
                (10, 300.0),
                (30, 600.0)
            ]
        else:
            pkgs = [
                (1, 70.0),
                (3, 120.0),
                (7, 200.0),
                (30, 500.0)
            ]

        for days, price in pkgs:
            c.execute("SELECT id FROM packages WHERE brand_id = ? AND duration_days = ?", (brand_id, days))
            p_row = c.fetchone()
            if not p_row:
                c.execute("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, 1)",
                          (brand_id, days, price))
                pkg_id = c.lastrowid
            else:
                pkg_id = p_row[0]
                c.execute("UPDATE packages SET price_inr = ? WHERE id = ?", (price, pkg_id))

            # Check stock
            c.execute("SELECT count(*) FROM keys_stock WHERE package_id = ? AND is_used = 0", (pkg_id,))
            stock_count = c.fetchone()[0]
            if stock_count < 5:
                # Add 5 active keys
                prefix = b["name"].split()[0].upper()[:4]
                for _ in range(5 - stock_count):
                    key_code = f"{prefix}-{days}D-{uuid.uuid4().hex[:8].upper()}"
                    c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)",
                              (pkg_id, key_code))

    conn.commit()
    conn.close()
    print("Successfully populated all 24 ANDROID NON ROOT brands, packages, and stock keys!")

if __name__ == "__main__":
    populate_non_root()
