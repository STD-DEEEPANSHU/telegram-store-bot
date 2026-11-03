import sqlite3

# ============================================================
# ⚡ EASILY CUSTOMIZE BRAND PRICES & VALIDITY HERE
# ============================================================
# Format: "Brand Name": [(days, price_inr), (days, price_inr), ...]

PRICE_LIST = {
    # PC Panels
    "BR_MODS PC ! + BYPASS": [
        (1, 120.0),
        (10, 499.0),
        (30, 999.0)
    ],
    
    # iPhone Panels
    "AIMHACK iOS": [
        (3, 400.0),
        (7, 899.0),
        (30, 1399.0)
    ],
    "TROLL iOS": [
        (3, 250.0),
        (7, 450.0),
        (15, 699.0),
        (30, 999.0)
    ],
    "ALPHA REGEDIT EXTERNAL": [
        (1, 120.0),
        (3, 200.0),
        (7, 350.0),
        (30, 999.0)
    ],

    # Android Root Panels
    "ZREX ROOT APK": [
        (1, 70.0),
        (3, 120.0),
        (7, 180.0)
    ],
    "Zytron Pro Apk": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "Angry Mod Apk": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "Xreg Safe Apk": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "Hikari Mod Apk": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "Lk Team Apk": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "Br Mods Apk": [
        (1, 90.0),
        (3, 160.0),
        (7, 270.0),
        (30, 650.0)
    ],
    "RAPID CORE ROOT": [
        (1, 85.0),
        (3, 160.0),
        (7, 260.0),
        (30, 620.0)
    ],
    "XYZ CHEATS ROOT": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "HEX BLADE ROOT APK": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "ROCKET MODS ROOT APK": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "DRIP CLIENT ROOT": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "INVISIBLE X EXTERNAL": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "HAXX-CKER PRO": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "ST MOD ROOT": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ],
    "SILENT CHEATS ROOT": [
        (1, 80.0),
        (3, 150.0),
        (7, 250.0),
        (30, 600.0)
    ]
}

def update_all_prices():
    import os
    db_file = os.path.join(os.path.dirname(__file__), "store.db")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    updated = 0
    for brand_name, packages in PRICE_LIST.items():
        c.execute("SELECT id FROM brands WHERE name = ?", (brand_name,))
        b_row = c.fetchone()
        if not b_row:
            continue
        brand_id = b_row["id"]

        # Delete existing packages for this brand to replace cleanly
        c.execute("DELETE FROM packages WHERE brand_id = ?", (brand_id,))
        for days, price in packages:
            c.execute("INSERT INTO packages (brand_id, duration_days, price_inr, hwid_device) VALUES (?, ?, ?, 1)", (brand_id, days, price))
            pkg_id = c.lastrowid
            # Ensure stock keys exist
            for i in range(1, 4):
                c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)", (pkg_id, f"KEY-{pkg_id}-{days}D-{i}XYZ"))
            updated += 1

    conn.commit()
    conn.close()
    print(f"Successfully updated {updated} packages across all brands with fresh keys!")

if __name__ == "__main__":
    update_all_prices()
