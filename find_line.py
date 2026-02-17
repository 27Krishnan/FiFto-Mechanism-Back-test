
input_path = r"E:\Backtest view report\index.html"
target_str = "function switchTab"

with open(input_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
for i, line in enumerate(lines):
    if target_str in line:
        print(f"Line {i+1}: {line.strip()}")
        found = True

if not found:
    print(f"String '{target_str}' not found.")
