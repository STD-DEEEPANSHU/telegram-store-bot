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

    # 42. PHANTOM [NON ROOT+ IOS]
    # 3H: 50->90, 12H: 90->170, 1D: 140->270, 3D: 190->370, 7D: 270->530, 15D: 450->890, 30D: 799->1588
    sync_brand(c, 42, "PHNTM", [
        (round(3/24, 4), "3 Hours", 90.0),
        (0.5, "12 Hours", 170.0),
        (1.0, "1 Days", 270.0),
        (3.0, "3 Days", 370.0),
        (7.0, "7 Days", 530.0),
        (15.0, "15 Days", 890.0),
        (30.0, "30 Days", 1588.0)
    ])

    # 43. RAPID CORE BOT NO ROOT
    # 1D: 75->140, 3D: 150->290, 7D: 250->490
    sync_brand(c, 43, "RPDBOT", [
        (1.0, "1 Days", 140.0),
        (3.0, "3 Days", 290.0),
        (7.0, "7 Days", 490.0)
    ])

    # 44. MYTH PANEL
    # 1H: 15->20, 3H: 45->80, 6H: 70->130, 12H: 90->170, 1D: 130->250, 3D: 170->330, 7D: 250->490, 14D: 499->988, 28D: 999->1988
    sync_brand(c, 44, "MYTH", [
        (round(1/24, 4), "1 Hours", 20.0),
        (round(3/24, 4), "3 Hours", 80.0),
        (0.25, "6 Hours", 130.0),
        (0.5, "12 Hours", 170.0),
        (1.0, "1 Days", 250.0),
        (3.0, "3 Days", 330.0),
        (7.0, "7 Days", 490.0),
        (14.0, "14 Days", 988.0),
        (28.0, "28 Days", 1988.0)
    ])

    conn.commit()
    conn.close()
    print("Successfully updated brands 42, 43, 44 packages and stock!")

if __name__ == "__main__":
    main()
