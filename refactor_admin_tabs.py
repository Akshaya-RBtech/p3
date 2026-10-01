import re

with open('templates/admin_dashboard.html', encoding='utf-8') as f:
    html = f.read()

# 1. Add Dashboard Tab at the top
html = html.replace('<!-- ============================== TAB 1 — MENU PLANNING ============================== -->', 
'''<!-- ============================== DASHBOARD ============================== -->
<div id="content-dashboard" class="tab-content block">
    <div class="card" style="padding:40px;text-align:center;margin-top:20px;max-width:600px;margin: 20px auto;border:none;">
        <i class="fas fa-chart-pie" style="font-size:54px;color:var(--primary);margin-bottom:16px;"></i>
        <h2 style="font-weight:800;color:var(--text-primary);">Welcome to your Dashboard</h2>
        <p style="color:var(--text-secondary);margin-top:8px;font-size:14px;line-height:1.5;">Select an option from the sidebar to manage menus, view analytics, and control hostel operations.</p>
    </div>
</div>

<!-- ============================== MENU MANAGEMENT ============================== -->''')

# Fix tab 1 block display
html = html.replace('id="content-menu" class="tab-content block"', 'id="content-menu" class="tab-content"')

# 2. Extract AI Meal Assistant into its own tab.
ai_marker = '''        <!-- AI Meal Assistant Section (Image 13) -->'''
weekly_marker = '''            <!-- Published menus table (Image 14) -->'''

# For Weekly Meal Calendar, it's inside the grid.
# Actually, if I just replace `<!-- Published menus table (Image 14) -->` with a close-grid, close-tab, and start new tab, like so:
html = html.replace(weekly_marker, '''        </div>
    </div>
    
    <!-- ============================== WEEKLY MEAL CALENDAR ============================== -->
    <div id="content-weekly" class="tab-content">
        <div class="grid grid-cols-1 gap-6">
            <!-- Published menus table (Image 14) -->''')

# 3. For AI Meal Assistant, it's currently at the same level as the grid, so we just close Weekly Meal Calendar and start AI
html = html.replace(ai_marker, '''        </div> <!-- End of content-weekly grid -->
    </div> <!-- Close content-weekly tab -->
    
    <!-- ============================== AI MEAL ASSISTANT ============================== -->
    <div id="content-aimenu" class="tab-content">
        <!-- AI Meal Assistant Section (Image 13) -->''')

# 4. Now what closes `content-aimenu`?
# The next tab in the file is Tab 5 — Communication Center? No, let's look at line 265 in original.
comms_marker = '''    <!-- ============================== TAB 5 — COMMUNICATION CENTER ============================== -->'''
html = html.replace(comms_marker, '''    </div> <!-- Close previous tab -->
''' + comms_marker)

# 5. Ops tab (line 351). It has multiple things inside it.
ops_marker_complaints = '''<!-- ============================== TAB X — STUDENT OPERATIONS ============================== -->'''
# Actually let's just make Attendance Tracker, Leave Requests, Complaints separate tabs.
html = html.replace('<div id="content-ops" class="tab-content">', '<div id="content-attendance" class="tab-content">')
# Inside content-ops, there's `<!-- Header Component -->` for Attendance? Let's check where Leave Request begins.

with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)
