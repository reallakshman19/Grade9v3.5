# scripts/clean_json_strings.py
import json
import re
from pathlib import Path

BANK_PATH = Path("TEST/physics-research/question_bank_kinematics_grade9.v1.json")
with open(BANK_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

def clean_val(val):
    if not isinstance(val, str):
        return val
    # Clean up corrupted patterns
    val = val.replace(r"$$\pi$", r"\pi")
    val = val.replace(r"$$ \pi$", r"\pi")
    val = val.replace(r"$ \pi$", r"\pi")
    val = val.replace(r"$\pi$", r"\pi")
    val = val.replace(r"$\Delta$", r"\Delta")
    val = val.replace(r"$\theta$", r"\theta")
    val = val.replace(r"$\omega$", r"\omega")
    val = re.sub(r'\\\$([a-zA-Z]+)\$', r'\\\1', val)
    val = val.replace(r"$$", "")
    return val

def traverse(node):
    if isinstance(node, str):
        return clean_val(node)
    elif isinstance(node, list):
        return [traverse(x) for x in node]
    elif isinstance(node, dict):
        return {k: traverse(v) for k, v in node.items()}
    return node

cleaned_data = traverse(data)

with open(BANK_PATH, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("[OK] Recursively cleaned all string values in question bank.")
