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

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. CTB MODS APK (brand_id 21)
    # Original: 12 Hours: 40, 1 Days: 50, 3 Days: 90, 7 Days: 250
    # New: 12H: 70, 1D: 90, 3D: 170, 7D: 490
    ctb_pkgs = [(0.5, 70.0), (1.0, 90.0), (3.0, 170.0), (7.0, 490.0)]
    existing_ctb = c.execute("SELECT id FROM packages WHERE brand_id = 21 ORDER BY id").fetchall()
    for idx, (dur, prc) in enumerate(ctb_pkgs):
        if idx < len(existing_ctb):
            pid = existing_ctb[idx][0]
            c.execute("UPDATE packages SET duration_days = ?, price_inr = ? WHERE id = ?", (dur, prc, pid))
        else:
            c.execute("INSERT INTO packages (brand_id, duration_days, price_inr) VALUES (21, ?, ?)", (dur, prc))
    if len(existing_ctb) > len(ctb_pkgs):
        for surplus in existing_ctb[len(ctb_pkgs):]:
            c.execute("DELETE FROM keys_stock WHERE package_id = ?", (surplus[0],))
            c.execute("DELETE FROM packages WHERE id = ?", (surplus[0],))

    # 2. ABCD PANEL (brand_id 22)
    # Original: 12 Hours: 49, 1 Days: 50, 3 Days: 100, 7 Days: 170
    # New: 12H: 88, 1D: 90, 3D: 190, 7D: 330
    abcd_pkgs = [(0.5, 88.0), (1.0, 90.0), (3.0, 190.0), (7.0, 330.0)]
    existing_abcd = c.execute("SELECT id FROM packages WHERE brand_id = 22 ORDER BY id").fetchall()
    for idx, (dur, prc) in enumerate(abcd_pkgs):
        if idx < len(existing_abcd):
            pid = existing_abcd[idx][0]
            c.execute("UPDATE packages SET duration_days = ?, price_inr = ? WHERE id = ?", (dur, prc, pid))
        else:
            c.execute("INSERT INTO packages (brand_id, duration_days, price_inr) VALUES (22, ?, ?)", (dur, prc))
    if len(existing_abcd) > len(abcd_pkgs):
        for surplus in existing_abcd[len(abcd_pkgs):]:
            c.execute("DELETE FROM keys_stock WHERE package_id = ?", (surplus[0],))
            c.execute("DELETE FROM packages WHERE id = ?", (surplus[0],))

    # 3. NINE X MOD (brand_id 23)
    # Original: 10 Days: 450, 15 Days: 600, 30 Days: 899
    # New: 10D: 890, 15D: 1190, 30D: 1788
    nine_pkgs = [(10.0, 890.0), (15.0, 1190.0), (30.0, 1788.0)]
    existing_nine = c.execute("SELECT id FROM packages WHERE brand_id = 23 ORDER BY id").fetchall()
    for idx, (dur, prc) in enumerate(nine_pkgs):
        if idx < len(existing_nine):
            pid = existing_nine[idx][0]
            c.execute("UPDATE packages SET duration_days = ?, price_inr = ? WHERE id = ?", (dur, prc, pid))
        else:
            c.execute("INSERT INTO packages (brand_id, duration_days, price_inr) VALUES (23, ?, ?)", (dur, prc))
    if len(existing_nine) > len(nine_pkgs):
        for surplus in existing_nine[len(nine_pkgs):]:
            c.execute("DELETE FROM keys_stock WHERE package_id = ?", (surplus[0],))
            c.execute("DELETE FROM packages WHERE id = ?", (surplus[0],))

    # 4. HG PROXY APK (brand_id 24)
    # Original: 1 Days: 90, 7 Days: 250, 10 Days: 300, 30 Days: 600
    # New: 1D: 170, 7D: 490, 10D: 590, 30D: 1190
    hg_pkgs = [(1.0, 170.0), (7.0, 490.0), (10.0, 590.0), (30.0, 1190.0)]
    existing_hg = c.execute("SELECT id FROM packages WHERE brand_id = 24 ORDER BY id").fetchall()
    for idx, (dur, prc) in enumerate(hg_pkgs):
        if idx < len(existing_hg):
            pid = existing_hg[idx][0]
            c.execute("UPDATE packages SET duration_days = ?, price_inr = ? WHERE id = ?", (dur, prc, pid))
        else:
            c.execute("INSERT INTO packages (brand_id, duration_days, price_inr) VALUES (24, ?, ?)", (dur, prc))
    if len(existing_hg) > len(hg_pkgs):
        for surplus in existing_hg[len(hg_pkgs):]:
            c.execute("DELETE FROM keys_stock WHERE package_id = ?", (surplus[0],))
            c.execute("DELETE FROM packages WHERE id = ?", (surplus[0],))

    # 5. ZREX APK [NON ROOT] (brand_id 31)
    # Original: 1D: 60, 3D: 100, 7D: 170
    # New: 1D: 110, 3D: 190, 7D: 330
    zrex_pkgs = [(1.0, 110.0), (3.0, 190.0), (7.0, 330.0)]
    existing_zrex = c.execute("SELECT id FROM packages WHERE brand_id = 31 ORDER BY id").fetchall()
    for idx, (dur, prc) in enumerate(zrex_pkgs):
        if idx < len(existing_zrex):
            pid = existing_zrex[idx][0]
            c.execute("UPDATE packages SET duration_days = ?, price_inr = ? WHERE id = ?", (dur, prc, pid))
        else:
            c.execute("INSERT INTO packages (brand_id, duration_days, price_inr) VALUES (31, ?, ?)", (dur, prc))

    # 6. For all other packages across all categories, apply the formula: (price * 2) - 10
    special_brands = (21, 22, 23, 24, 31)
    other_pkgs = c.execute("SELECT id, price_inr FROM packages WHERE brand_id NOT IN (?, ?, ?, ?, ?)", special_brands).fetchall()
    for pid, old_prc in other_pkgs:
        new_prc = round((old_prc * 2) - 10, 2)
        if new_prc <= 0:
            new_prc = old_prc
        c.execute("UPDATE packages SET price_inr = ? WHERE id = ?", (new_prc, pid))

    conn.commit()

    # 7. Stock Keys check & replenishment
    all_packages = c.execute("SELECT p.id, b.name, p.duration_days FROM packages p JOIN brands b ON p.brand_id = b.id").fetchall()
    total_added = 0
    for pid, bname, dur in all_packages:
        avail_cnt = c.execute("SELECT COUNT(*) FROM keys_stock WHERE package_id = ? AND is_used = 0", (pid,)).fetchone()[0]
        needed = 10 - avail_cnt
        if needed > 0:
            clean_bname = ''.join(c for c in bname if c.isalnum())[:4].upper()
            dur_lbl = "12H" if dur in (0, 0.5) else f"{int(dur)}D"
            for _ in range(needed):
                k = generate_key_code(f"{clean_bname}-{dur_lbl}")
                c.execute("INSERT INTO keys_stock (package_id, license_key, is_used) VALUES (?, ?, 0)", (pid, k))
                total_added += 1

    conn.commit()
    conn.close()
    print(f"Successfully updated all package prices and ensured stock. Added {total_added} fresh keys.")

if __name__ == "__main__":
    main()
