import sqlite3
import random
import string
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "store.db")

def generate_key_code(prefix="KEY"):
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{part1}-{part2}-{part3}"

def sync_brand_packages(c, brand_id, bname, pkg_defs):
    """
    pkg_defs: list of tuples (duration_days, duration_label, price_inr)
    """
    existing = c.execute("SELECT id FROM packages WHERE brand_id = ? ORDER BY id", (brand_id,)).fetchall()
    active_ids = []
    for idx, (dur, label, prc) in enumerate(pkg_defs):
        if idx < len(existing):
            pid = existing[idx][0]
            c.execute("UPDATE packages SET duration_days = ?, duration_label = ?, price_inr = ? WHERE id = ?",
                      (dur, label, prc, pid))
            active_ids.append(pid)
        else:
            c.execute("INSERT INTO packages (brand_id, duration_days, duration_label, price_inr) VALUES (?, ?, ?, ?)",
                      (brand_id, dur, label, prc))
            active_ids.append(c.lastrowid)

    if len(existing) > len(pkg_defs):
        for surplus in existing[len(pkg_defs):]:
            c.execute("DELETE FROM keys_stock WHERE package_id = ?", (surplus[0],))
            c.execute("DELETE FROM packages WHERE id = ?", (surplus[0],))

    # Ensure stock keys
    for pid in active_ids:
        avail_cnt = c.execute("SELECT COUNT(*) FROM keys_stock WHERE package_id = ? AND is_used = 0", (pid,)).fetchone()[0]
        needed = 10 - avail_cnt
        if needed > 0:
            clean_bname = ''.join(ch for ch in bname if ch.isalnum())[:4].upper()
            row = c.execute("SELECT duration_label FROM packages WHERE id = ?", (pid,)).fetchone()
            dur_tag = ''.join(ch for ch in (row[0] or "KEY") if ch.isalnum())
            for _ in range(needed):
                k = generate_key_code(f"{clean_bname}-{dur_tag}")
                c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)", (pid, k))

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. CTB MODS APK (21)
    # Orig: 12H: 40, 1D: 50, 3D: 90, 7D: 250 -> Formula: (P*2)-10
    ctb = [
        (0.5, "12 Hours", 70.0),
        (1.0, "1 Days", 90.0),
        (3.0, "3 Days", 170.0),
        (7.0, "7 Days", 490.0)
    ]
    sync_brand_packages(c, 21, "CTB", ctb)

    # 2. ABCD PANEL (22)
    # Orig: 12H: 49, 1D: 50, 3D: 100, 7D: 170 -> Formula: (P*2)-10
    abcd = [
        (0.5, "12 Hours", 88.0),
        (1.0, "1 Days", 90.0),
        (3.0, "3 Days", 190.0),
        (7.0, "330.0", 330.0)
    ]
    # fix label for 7D
    abcd[3] = (7.0, "7 Days", 330.0)
    sync_brand_packages(c, 22, "ABCD", abcd)

    # 3. NINE X MOD (23)
    # Orig: 10D: 450, 15D: 600, 30D: 899 -> Formula: (P*2)-10
    nine = [
        (10.0, "10 Days", 890.0),
        (15.0, "15 Days", 1190.0),
        (30.0, "30 Days", 1788.0)
    ]
    sync_brand_packages(c, 23, "NINEX", nine)

    # 4. HG PROXY APK (24)
    # Orig: 1D: 90, 7D: 250, 10D: 300, 30D: 600 -> Formula: (P*2)-10
    hg = [
        (1.0, "1 Days", 170.0),
        (7.0, "7 Days", 490.0),
        (10.0, "10 Days", 590.0),
        (30.0, "30 Days", 1190.0)
    ]
    sync_brand_packages(c, 24, "HGPRX", hg)

    # 5. PATOTEAM ORANGE (25)
    # Orig: 3D: 240, 7D: 350, 15D: 600, 30D: 950 -> Formula: (P*2)-10
    pato_o = [
        (3.0, "3 Days", 470.0),
        (7.0, "7 Days", 690.0),
        (15.0, "15 Days", 1190.0),
        (30.0, "30 Days", 1890.0)
    ]
    sync_brand_packages(c, 25, "PATO_O", pato_o)

    # 6. PATOTEAM BLUE (26)
    # Orig: 3D: 175, 15D: 520, 30D: 850 -> Formula: (P*2)-10
    pato_b = [
        (3.0, "3 Days", 340.0),
        (15.0, "15 Days", 1030.0),
        (30.0, "30 Days", 1690.0)
    ]
    sync_brand_packages(c, 26, "PATO_B", pato_b)

    # 7. BR MODS NON ROOT (27)
    # Orig: 80: 50, 7D: 250, 15D: 350 -> Formula: (P*2)-10
    br_mods = [
        (0.1, "80", 90.0),
        (7.0, "7 Days", 490.0),
        (15.0, "15 Days", 690.0)
    ]
    sync_brand_packages(c, 27, "BRMOD", br_mods)

    # 8. DRIP WIRE EXTRNAL APK (28)
    # Orig: 6H: 50, 12H: 70, 1D: 150, 7D: 350 -> Formula: (P*2)-10
    drip_wire = [
        (0.25, "6 Hours", 90.0),
        (0.5, "12 Hours", 130.0),
        (1.0, "1 Days", 290.0),
        (7.0, "7 Days", 690.0)
    ]
    sync_brand_packages(c, 28, "DRIPW", drip_wire)

    # 9. SILENT CHEATS PROXY APK (29)
    # Orig: 12H: 70, 3D: 199, 7D: 500, 30D: 980 -> Formula: (P*2)-10
    silent = [
        (0.5, "12 Hours", 130.0),
        (3.0, "3 Days", 388.0),
        (7.0, "7 Days", 990.0),
        (30.0, "30 Days", 1950.0)
    ]
    sync_brand_packages(c, 29, "SILNT", silent)

    conn.commit()
    conn.close()
    print("Successfully synchronized all 9 brands packages and prices!")

if __name__ == "__main__":
    main()
