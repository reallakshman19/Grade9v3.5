# scripts/find_unrendered_math.py
import re
from pathlib import Path

target = Path("standalone/practice/core2-physics-kinematics-grade9-master.html")
html = target.read_text(encoding="utf-8")

clean = re.sub(r'<script[\s\S]*?</script>', '', html)
clean = re.sub(r'<style[\s\S]*?</style>', '', clean)
clean = re.sub(r'<svg[\s\S]*?</svg>', '', clean)
clean = re.sub(r'<annotation[\s\S]*?</annotation>', '', clean)

matches = list(re.finditer(r'\$([^\$]{1,200})\$', clean))
print(f"Total raw $ matches: {len(matches)}")
for i, m in enumerate(matches):
    start = max(0, m.start() - 50)
    end = min(len(clean), m.end() + 50)
    print(f"--- #{i+1} ---")
    print(clean[start:end].replace('\n', ' '))
