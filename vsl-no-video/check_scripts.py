import re, subprocess, sys, os

with open("index.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

# Find all <script ...>...</script> blocks that do NOT have a src= attribute (inline JS only)
blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, flags=re.S | re.I)

print(f"Found {len(blocks)} inline <script> blocks (no src)")

os.makedirs("_check_tmp", exist_ok=True)
errors = 0
for i, code in enumerate(blocks):
    code = code.strip()
    if not code:
        continue
    path = f"_check_tmp/s{i}.js"
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
    if r.returncode != 0:
        errors += 1
        print(f"--- SYNTAX ERROR in block {i} (len={len(code)}) ---")
        print(r.stderr[:1000])
        print("First 300 chars of block:", code[:300])
        print("Last 300 chars of block:", code[-300:])

print(f"\nTOTAL SYNTAX ERRORS: {errors}")
