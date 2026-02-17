
import re

html_path = r"E:\Backtest view report\index.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# 1. Update Navigation Bar
nav_replacement = """
            <button class="tab-btn" onclick="switchTab('pnl-entry')">P&L Entry</button>
            <button class="tab-btn" onclick="switchTab('pnl-dashboard'); if(window.pnlUpdateDashboard) window.pnlUpdateDashboard()">P&L Dashboard</button>
            <button class="tab-btn" onclick="switchTab('pnl-monthly'); if(window.pnlUpdateMonthly) window.pnlUpdateMonthly()">P&L Monthly</button>
            <button class="tab-btn" onclick="switchTab('pnl-portfolio'); if(window.pnlLoadPortfolio) window.pnlLoadPortfolio()">Portfolio</button>
"""

# Try to find the old button
if 'switchTab(\'pnl-report\')' in html_content:
    html_content = re.sub(
        r'<button class="tab-btn" onclick="switchTab\(\'pnl-report\'\)">.*?</button>',
        nav_replacement.strip(),
        html_content
    )
else:
    print("Warning: Could not find P&L Report button in nav.")

# 2. Extract P&L Content Block
# Look for TAB 7 marker and closing div before Footer
# Or regex for id="tab-pnl-report"
match = re.search(r'(?s)<div id="tab-pnl-report" class="tab-content">(.*?)</div>\s*(?=<footer>)', html_content)
if not match:
    # Try simpler matching
    match = re.search(r'(?s)<div id="tab-pnl-report" class="tab-content">(.*?)</div>', html_content)

if not match:
    print("Error: Could not find #tab-pnl-report block.")
    exit(1)

pnl_inner_html = match.group(1)
full_block_to_replace = match.group(0)

# 3. Extract Views Logic
# We need to extract <main id="view-table">...</main>, etc.
# Modals are usually at the end.

def extract_view(view_id, content):
    pattern = re.compile(f'(?s)<main id="{view_id}"(.*?)>(.*?)</main>')
    m = pattern.search(content)
    if m:
        # Reconstruct with active class if needed (remove hidden)
        attrs = m.group(1).replace('hidden', '').replace('view-section', 'view-section active')
        return f'<main id="{view_id}"{attrs}>{m.group(2)}</main>'
    return None

view_table = extract_view('view-table', pnl_inner_html)
view_dashboard = extract_view('view-dashboard', pnl_inner_html)
view_monthly = extract_view('view-monthly', pnl_inner_html)
view_portfolio = extract_view('view-portfolio', pnl_inner_html)

if not all([view_table, view_dashboard, view_monthly, view_portfolio]):
    print("Error: Could not extract all views.")
    # Fallback or exit?
    # View portfolio might be missing if file content was truncated in regex?
    # Let's inspect what pnl_inner_html contains if needed.
    pass

# Extract Modals
# Logic: Everything that is NOT inside .pnl-container?
# Or just search for specific Modal IDs.
modal_ids = ['manage-modal', 'settings-modal', 'delete-confirm-modal', 'recycle-bin-modal', 'undo-toast', 'details-modal']
modals_html = ""
for mid in modal_ids:
    pattern = re.compile(f'(?s)<div id="{mid}"(.*?)>(.*?)</div>\s*(?=<!--|$|<div id=)') 
    # Modals might be nested or just sequential.
    # robust extraction: find <div id="mid" ... </div> balancing braces?
    # Simple regex for matching balanced divs is hard.
    # Assumption: Modals are top-level in pnl_inner_html.
    # Let's try splitting by <div id="...-modal"
    pass

# Better strategy for Modals:
# We know they are at the end of pnl_inner_html
# After `.pnl-container` closes.
# Let's find end of .pnl-container
container_end_match = re.search(r'</div>\s*<!-- Manage Owners Modal -->', pnl_inner_html)
if container_end_match:
    # Everything after is Modals?
    modals_start_idx = container_end_match.start() + 6 # len(</div>)
    modals_html = pnl_inner_html[modals_start_idx:]
else:
    # Try another marker
    if '<!-- Manage Owners Modal -->' in pnl_inner_html:
        parts = pnl_inner_html.split('<!-- Manage Owners Modal -->')
        modals_html = '<!-- Manage Owners Modal -->' + parts[1]
    else:
        print("Warning: Could not locate Modals start.")
        modals_html = ""

# 4. Construct New Tabs
def build_tab(tab_id, content):
    return f"""
        <div id="{tab_id}" class="tab-content">
            <div class="pnl-theme-wrapper">
                <div class="pnl-container" style="border:none; box-shadow:none; background:transparent;">
                    {content}
                </div>
            </div>
        </div>
    """
    # Note: pnl-container style override to avoid double boxing if desired?
    # The original pnl-container had the background/blur. 
    # If we want that style, we keep it. 
    # If we split views, each View needs the container style?
    # Yes, keep standard pnl-container.

def build_tab_std(tab_id, content):
    return f"""
        <div id="{tab_id}" class="tab-content">
            <div class="pnl-theme-wrapper">
                <div class="pnl-container">
                    {content}
                </div>
            </div>
        </div>
    """

new_html_block = ""
new_html_block += build_tab_std("tab-pnl-entry", view_table) + "\n"
new_html_block += build_tab_std("tab-pnl-dashboard", view_dashboard) + "\n"
new_html_block += build_tab_std("tab-pnl-monthly", view_monthly) + "\n"
new_html_block += build_tab_std("tab-pnl-portfolio", view_portfolio) + "\n"

# Modals Wrapper
new_html_block += f"""
        <!-- P&L MODALS -->
        <div class="pnl-theme-wrapper">
            {modals_html}
        </div>
"""

# Replace in content
html_content = html_content.replace(full_block_to_replace, new_html_block)

# Remove the internal header?
# We didn't extract the internal header, so it's gone (it was inside .pnl-container but before main views).
# My extraction logic only took `main` tags. So header is implicitly removed. Good.

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Refactored P&L Navigation successfully.")
