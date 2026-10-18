# scripts/upgrade_svg_fonts.py
import re
from pathlib import Path

target = Path("scripts/compile_tri_modal_kinematics_master_app.py")
text = target.read_text(encoding="utf-8")

def fix_font_size(m):
    val = int(m.group(1))
    if val < 14:
        return 'font-size="14"'
    return m.group(0)

new_text = re.sub(r'font-size="(\d+)"', fix_font_size, text)
target.write_text(new_text, encoding="utf-8")
print(f"[OK] Upgraded SVG font sizes in {target}")
