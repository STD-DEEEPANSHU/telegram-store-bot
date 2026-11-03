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

def sync_brand(c, brand_id, bname, pkg_defs):
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

    # Replenish stock keys
    for pid in active_ids:
        avail = c.execute("SELECT COUNT(*) FROM keys_stock WHERE package_id = ? AND is_used = 0", (pid,)).fetchone()[0]
        needed = 10 - avail
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

    # 1. TROLL MODZ APK (33)
    # Orig: 6H: 60, 12H: 80, 1D: 120, 3D: 170, 7D: 390, 15D: 699 -> (P*2)-10
    troll_pkgs = [
        (0.25, "6 Hours", 110.0),
        (0.5, "12 Hours", 150.0),
        (1.0, "1 Days", 230.0),
        (3.0, "3 Days", 330.0),
        (7.0, "7 Days", 770.0),
        (15.0, "15 Days", 1388.0)
    ]
    sync_brand(c, 33, "TROLL", troll_pkgs)

    # 2. HEX BLADE APK MOD (34)
    # Orig: 1D: 90, 7D: 250, 15D: 599, 30D: 899 -> (P*2)-10
    hex_pkgs = [
        (1.0, "1 Days", 170.0),
        (7.0, "7 Days", 490.0),
        (15.0, "15 Days", 1188.0),
        (30.0, "30 Days", 1788.0)
    ]
    sync_brand(c, 34, "HEXBLD", hex_pkgs)

    # 3. RAPID CORE APKMOD [NON ROOT] (35)
    # Orig: 1D: 80, 7D: 240, 15D: 450, 30D: 799 -> (P*2)-10
    rapid_pkgs = [
        (1.0, "1 Days", 150.0),
        (7.0, "7 Days", 470.0),
        (15.0, "15 Days", 890.0),
        (30.0, "30 Days", 1588.0)
    ]
    sync_brand(c, 35, "RAPID", rapid_pkgs)

    # 4. PRIME MODS APK (36)
    # Orig: 1D: 75, 3D: 170, 7D: 280 -> (P*2)-10
    prime_pkgs = [
        (1.0, "1 Days", 140.0),
        (3.0, "3 Days", 330.0),
        (7.0, "7 Days", 550.0)
    ]
    sync_brand(c, 36, "PRIME", prime_pkgs)

    # 5. SILENT CHEATS APKMOD (37)
    # Orig: 1D: 85, 3D: 170, 7D: 260, 15D: 499 -> (P*2)-10
    silent_pkgs = [
        (1.0, "1 Days", 160.0),
        (3.0, "3 Days", 330.0),
        (7.0, "7 Days", 510.0),
        (15.0, "15 Days", 988.0)
    ]
    sync_brand(c, 37, "SILNTA", silent_pkgs)

    conn.commit()
    conn.close()
    print("Successfully updated brands 33 to 37 packages and stock!")

if __name__ == "__main__":
    main()
