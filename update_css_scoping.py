
import re

css_path = r"E:\Backtest view report\pnl_style.css"

with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

# Replace all occurrences of #tab-pnl-report with .pnl-theme-wrapper
# We use regex to ensure we don't accidentally replace partial words if any (unlikely with IDs but safe)
# Actually, simple string replacement is safer for CSS selectors.
new_css_content = css_content.replace("#tab-pnl-report", ".pnl-theme-wrapper")

with open(css_path, "w", encoding="utf-8") as f:
    f.write(new_css_content)

print("Replaced #tab-pnl-report with .pnl-theme-wrapper in pnl_style.css")
