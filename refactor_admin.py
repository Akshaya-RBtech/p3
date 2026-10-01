import re

with open('templates/admin_dashboard.html', encoding='utf-8') as f:
    text = f.read()

# 1. Add Dashboard content container right at start (line 58ish before TAB 1)
dashboard_marker = r'<!-- ============================== TAB 1 — MENU PLANNING ============================== -->'
dashboard_replacement = r'''<!-- ============================== DASHBOARD ============================== -->
<div id="content-dashboard" class="tab-content block">
    <div class="card" style="padding:24px;text-align:center;margin-top:20px;">
        <i class="fas fa-chart-pie" style="font-size:48px;color:var(--primary);margin-bottom:16px;"></i>
        <h2>Welcome to the Admin Dashboard</h2>
        <p style="color:var(--text-secondary);margin-top:8px;">Please select an option from the sidebar to view specific features.</p>
    </div>
</div>

<!-- ============================== TAB 1 — MENU PLANNING ============================== -->'''
text = text.replace(dashboard_marker, dashboard_replacement)

# Make sure old 'content-menu' is NOT block by default, so it's `class="tab-content"`
text = text.replace('id="content-menu" class="tab-content block"', 'id="content-menu" class="tab-content"')

# 2. Split Weekly Meal Calendar from Menu
# Line 98 has `<!-- Published menus table (Image 14) -->`
weekly_marker = r'<!-- Published menus table (Image 14) -->'
weekly_replacement = r'''
        </div> <!-- End of content-menu grid -->
    </div> <!-- End of content-menu -->

    <!-- ============================== WEEKLY MEAL CALENDAR ============================== -->
    <div id="content-weekly" class="tab-content">
        <!-- Published menus table (Image 14) -->'''
text = text.replace(weekly_marker, weekly_replacement)

# 3. Split AI Assistant from Weekly menu (Line 182 has `<!-- AI Meal Assistant Section (Image 13) -->`)
# wait, if I closed content-menu grid and content-menu above, Weekly is open. I don't have a grid closing tag. 
# actually wait, `content-weekly` needs its own layout.

# I will write a more precise HTML parsing logic or string replace logic that ensures valid HTML.
