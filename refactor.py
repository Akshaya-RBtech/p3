import os
import re

def refactor_admin():
    path = 'templates/admin_dashboard.html'
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Step 1: Flatten everything by removing the current tab-content block divs
    text = re.sub(r'<!-- ============================== TAB 1 — MENU PLANNING ============================== -->\s*<div id=\"content-menu\" class=\"tab-content block\">\s*<div class=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">',
                  r'<!-- ============================== MENU PLANNING ============================== -->\n<div id="content-menu_mgmt" class="tab-content block">\n<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">', text)

    # Let's write a targeted script to parse and split div clusters, or I can just print the exact sections!
    
refactor_admin()
