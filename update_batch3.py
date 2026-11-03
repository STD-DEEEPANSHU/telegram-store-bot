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

    # 1. BALA MODS APK (30)
    # 1H: 17->24, 2H: 35->60, 3H: 65->120, 4H: 90->170, 5H: 120->230, 6H: 90->170, 7H: 145->280, 10H: 140->270
    bala_pkgs = [
        (round(1/24, 4), "1 Hours", 24.0),
        (round(2/24, 4), "2 Hours", 60.0),
        (round(3/24, 4), "3 Hours", 120.0),
        (round(4/24, 4), "4 Hours", 170.0),
        (round(5/24, 4), "5 Hours", 230.0),
        (round(6/24, 4), "6 Hours", 170.0),
        (round(7/24, 4), "7 Hours", 280.0),
        (round(10/24, 4), "10 Hours", 270.0)
    ]
    sync_brand(c, 30, "BALA", bala_pkgs)

    # 2. ZREX APK [NON ROOT] (31)
    # 1D: 60->110, 3D: 100->190, 7D: 170->330
    zrex_pkgs = [
        (1.0, "1 Days", 110.0),
        (3.0, "3 Days", 190.0),
        (7.0, "7 Days", 330.0)
    ]
    sync_brand(c, 31, "ZREX", zrex_pkgs)

    # 3. XYZ [NON ROOT] (32)
    # 1H: 25->40, 2H: 45->80, 4H: 65->120, 6H: 90->170, 12H: 140->270
    # 1D: 200->390, 3D: 450->890, 7D: 700->1390, 30D: 999->1988
    xyz_pkgs = [
        (round(1/24, 4), "1 Hours", 40.0),
        (round(2/24, 4), "2 Hours", 80.0),
        (round(4/24, 4), "4 Hours", 120.0),
        (round(6/24, 4), "6 Hours", 170.0),
        (0.5, "12 Hours", 270.0),
        (1.0, "1 Days", 390.0),
        (3.0, "3 Days", 890.0),
        (7.0, "7 Days", 1390.0),
        (30.0, "30 Days", 1988.0)
    ]
    sync_brand(c, 32, "XYZ", xyz_pkgs)

    conn.commit()
    conn.close()
    print("Successfully updated brands 30, 31, 32 packages and stock!")

if __name__ == "__main__":
    main()
