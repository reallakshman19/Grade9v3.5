# scripts/sanitize_latex_tokens.py
import re
from pathlib import Path

BANK_PATH = Path("TEST/physics-research/question_bank_kinematics_grade9.v1.json")
text = BANK_PATH.read_text(encoding="utf-8")

# Fix corrupted nested tokens
text = text.replace(r"\$\$\pi$", r"\pi")
text = text.replace(r"\$\pi$", r"\pi")
text = text.replace(r"\$\Delta$", r"\Delta")
text = text.replace(r"\$\theta$", r"\theta")
text = text.replace(r"\$\omega$", r"\omega")
text = text.replace(r"$\$", r"")
text = text.replace(r"$$", r"")
text = re.sub(r'\\\$([a-zA-Z]+)\$', r'\\\1', text)

BANK_PATH.write_text(text, encoding="utf-8")
print(f"[OK] Sanitized corrupted tokens in {BANK_PATH}")
