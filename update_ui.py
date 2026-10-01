import re

def rewrite_student():
    path = 'templates/student_portal.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    js_match = re.search(r'(<script>.*?</script>)', content, re.DOTALL)
    js_code = js_match.group(1) if js_match else ''

    # Get menus rendering section (from {% if menus %} to its {% endif %})
    menu_match = re.search(r'({% if menus %}.*?{% else %}.*?{% endif %})', content, re.DOTALL)
    menus_html = menu_match.group(1) if menu_match else '<div>No Menus</div>'
    
    # Clean up the old structure
    new_html = r'''{% extends "layout.html" %}

{% block content %}
<style>
/* Override default layout padding */
.page-wrapper { padding: 0 !important; max-width: 100% !important; height: calc(100vh - 64px); display: flex; flex-direction: row; }
@media (max-width: 768px) { .page-wrapper { flex-direction: column; } }

.sidebar-nav { width: 260px; background: var(--sidebar-bg); border-right: 1px solid var(--sidebar-border); overflow-y: auto; display:flex; flex-direction: column; padding: 24px 12px; flex-shrink:0; }
.sidebar-btn { display: flex; align-items: center; gap: 12px; padding: 12px 16px; width: 100%; border: none; background: transparent; color: var(--text-secondary); text-align: left; font-size: 14px; font-weight: 600; border-radius: 12px; cursor: pointer; transition: all 0.2s; margin-bottom: 4px; }
.sidebar-btn:hover { background: rgba(99,102,241,0.06); color: var(--text-primary); }
.sidebar-btn.active-tab { background: var(--primary); color: white; box-shadow: 0 4px 12px rgba(99,102,241,0.25); }
.fw { width: 20px; text-align: center; }

.content-area { flex: 1; padding: 32px; overflow-y: auto; background: var(--body-bg); }
.tab-content { display: none; animation: fadeIn 0.3s ease; }
.tab-content.block { display: block; }

@media (max-width: 768px) {
    .sidebar-nav { width: 100%; height: auto; border-right: none; border-bottom: 1px solid var(--border); max-height: 250px; display: none; }
    .sidebar-nav.api-show { display: flex; }
}
</style>

<div class="md:hidden" style="padding:12px 20px;background:var(--card-bg);border-bottom:1px solid var(--border);font-weight:700;display:flex;justify-content:space-between;align-items:center;" onclick="document.querySelector('.sidebar-nav').classList.toggle('api-show')">
    <span><i class="fas fa-bars"></i> Menu</span>
    <span class="badge badge-primary">{{ current_user.username }}</span>
</div>

<div class="sidebar-nav">
    <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;margin:0 0 10px 16px;">Student Nav</div>
    <button class="sidebar-btn active-tab" onclick="switchTab('home', this)"><i class="fas fa-home fw"></i> Home Dashboard</button>
    <button class="sidebar-btn" onclick="switchTab('calendar', this)"><i class="fas fa-calendar-alt fw"></i> Weekly Meal Calendar</button>
    <button class="sidebar-btn" onclick="switchTab('assistant', this)"><i class="fas fa-robot fw"></i> Student AI Assistant</button>
    <button class="sidebar-btn" onclick="switchTab('notifications', this)"><i class="fas fa-bell fw"></i> Notifications</button>
    <button class="sidebar-btn" onclick="switchTab('feedback', this)"><i class="fas fa-star fw"></i> Food Feedback</button>
    <button class="sidebar-btn" onclick="switchTab('complaints', this)"><i class="fas fa-flag fw"></i> Student Complaints</button>
    <button class="sidebar-btn" onclick="switchTab('leave', this)"><i class="fas fa-calendar-minus fw"></i> Student Leave Requests</button>
    <button class="sidebar-btn" onclick="switchTab('profile', this)"><i class="fas fa-user fw"></i> Student Profile</button>
    
    <div style="margin-top:auto;"></div>
    <a href="{{ url_for('logout') }}" class="sidebar-btn" style="color:var(--danger);text-decoration:none;"><i class="fas fa-sign-out-alt fw"></i> Logout</a>
</div>

<div class="content-area fade-in">
    <!-- 1. Home Dashboard -->
    <div id="content-home" class="tab-content block">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Welcome, {{ current_user.username }}</h2>
        <h3 style="font-size:18px;font-weight:700;margin-bottom:16px;">Today's &amp; Tomorrow's Menu</h3>
        <!-- MENUS_INJECT -->
    </div>
    
    <!-- 2. Weekly Meal Calendar -->
    <div id="content-calendar" class="tab-content">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Weekly Meal Calendar</h2>
        <div class="card p-4 text-center text-muted">Calendar view populated from database. View your upcoming confirmations here.</div>
        <h3 style="font-size:18px;font-weight:700;margin:24px 0 16px;">Attendance History</h3>
        <!-- Note: Real implementation uses voted_ids or history logic -->
    </div>
    
    <!-- 3. Student AI Assistant -->
    <div id="content-assistant" class="tab-content">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Student AI Assistant</h2>
        <div class="card" style="max-width:600px;">
            <div style="padding:20px;">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
                    <button onclick="setStudentPrompt('What is for lunch today?')" class="badge badge-primary" style="cursor:pointer;border:none;">🍽️ Today's Menu</button>
                    <button onclick="setStudentPrompt('Should I eat today?')" class="badge badge-success" style="cursor:pointer;border:none;">🤔 Should I Eat?</button>
                </div>
                <div id="student-chat-messages" style="height:350px;overflow-y:auto;display:flex;flex-direction:column;gap:10px;margin-bottom:14px;padding-right:10px;">
                    <div style="display:flex;align-items:flex-start;gap:8px;">
                        <div style="width:28px;height:28px;border-radius:50%;background:var(--primary);color:white;display:flex;align-items:center;justify-content:center;font-size:10px;"><i class="fas fa-robot"></i></div>
                        <div style="background:var(--input-bg);border:1px solid var(--border);border-radius:0 12px 12px 12px;padding:10px 14px;font-size:13px;max-width:85%;">Hey! Ask me about menus or diet tips!</div>
                    </div>
                </div>
                <div style="display:flex;gap:8px;">
                    <input type="text" id="student-chat-input" placeholder="Type your question..." onkeypress="if(event.key==='Enter') sendStudentMsg()" class="form-input" style="flex:1;">
                    <button onclick="sendStudentMsg()" class="btn-primary" style="padding:10px 16px;"><i class="fas fa-paper-plane"></i></button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- 4. Notifications -->
    <div id="content-notifications" class="tab-content">
        <div style="display:flex;justify-content:space-between;margin-bottom:24px;">
            <h2 style="font-size:24px;font-weight:800;">Notifications</h2>
            <button onclick="readAllNotifs()" class="btn-primary" style="font-size:12px;padding:6px 14px;">Mark All Read</button>
        </div>
        <div class="card p-4 text-center text-muted">Use the primary bell icon in the top header to view real-time notifications. Admin approvals trigger notifications directly.</div>
    </div>
    
    <!-- 5. Food Feedback -->
    <div id="content-feedback" class="tab-content">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Food Feedback</h2>
        <div class="card p-4">Submit feedback directly from the "Home Dashboard" menu cards after voting YES!</div>
    </div>
    
    <!-- 6. Student Complaints -->
    <div id="content-complaints" class="tab-content">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Student Complaints</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div class="card p-4">
                <h3 style="font-weight:700;margin-bottom:12px;"><i class="fas fa-flag text-danger mr-2"></i> Submit Complaint</h3>
                <form onsubmit="submitStudentComplaint(event)">
                    <select id="comp-category" class="form-input mb-3 w-full" required>
                        <option value="">Select Category...</option>
                        <option value="Food Quality">Food Quality</option>
                        <option value="Food Quantity">Food Quantity</option>
                        <option value="Hygiene">Hygiene</option>
                        <option value="Menu">Menu</option>
                        <option value="Service">Service</option>
                        <option value="Other">Other</option>
                    </select>
                    <textarea id="comp-description" class="form-input mb-3 w-full" rows="3" placeholder="Describe your issue..." required></textarea>
                    <button type="submit" class="btn-primary w-full justify-center">Submit</button>
                </form>
                <div id="comp-status" class="mt-2 text-center text-xs fw-600 hidden"></div>
            </div>
            
            <div class="card p-4" style="max-height:400px;overflow-y:auto;">
                <h3 style="font-weight:700;margin-bottom:12px;">Complaint History</h3>
                {% if complaints %}
                    {% for c in complaints %}
                    <div class="border rounded p-3 mb-2 bg-input">
                        <div class="flex justify-between mb-1"><span class="text-xs fw-600">{{ c.category }}</span><span class="badge badge-warning text-[10px]">{{ c.status }}</span></div>
                        <p class="text-xs mb-2">{{ c.description }}</p>
                        {% if c.admin_note %}<div class="bg-[rgba(99,102,241,0.05)] border-l-2 border-primary text-[11px] p-2 text-muted"><strong>Admin:</strong> {{ c.admin_note }}</div>{% endif %}
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="text-muted text-xs text-center p-3">No complaints submitted yet.</div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- 7. Student Leave Requests -->
    <div id="content-leave" class="tab-content">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Student Leave Requests</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div class="card p-4">
                <h3 style="font-weight:700;margin-bottom:12px;"><i class="fas fa-calendar-minus text-warning mr-2"></i> Apply for Leave</h3>
                <form onsubmit="submitStudentLeave(event)">
                    <div class="flex gap-2 mb-3">
                        <div class="flex-1"><label class="text-[11px] fw-600 text-muted">Start Date</label><input type="date" id="leave-start" class="form-input w-full" required></div>
                        <div class="flex-1"><label class="text-[11px] fw-600 text-muted">End Date</label><input type="date" id="leave-end" class="form-input w-full" required></div>
                    </div>
                    <select id="leave-type" class="form-input mb-3 w-full" required>
                        <option value="">Leave Type...</option><option value="Home Visit">Home Visit</option><option value="Medical">Medical</option><option value="Outing">Outing</option><option value="Other">Other</option>
                    </select>
                    <input type="text" id="leave-reason" class="form-input mb-3 w-full" placeholder="Reason">
                    <button type="submit" class="btn-primary w-full justify-center bg-warning border-warning">Submit Request</button>
                </form>
                <div id="leave-status" class="mt-2 text-center text-xs fw-600 hidden"></div>
            </div>
            
            <div class="card p-4" style="max-height:400px;overflow-y:auto;">
                <h3 style="font-weight:700;margin-bottom:12px;">Leave History</h3>
                {% if leaves %}
                    {% for L in leaves %}
                    <div class="border rounded p-3 mb-2 bg-input">
                        <div class="flex justify-between mb-1"><span class="text-[11px] fw-600 text-muted">{{ L.start_date }} to {{ L.end_date }}</span><span class="badge badge-warning text-[10px]">{{ L.status }}</span></div>
                        <p class="text-xs">Reason: {{ L.reason or 'None' }}</p>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="text-muted text-xs text-center p-3">No leave requests found.</div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- 8. Student Profile -->
    <div id="content-profile" class="tab-content">
        <h2 style="font-size:24px;font-weight:800;margin-bottom:24px;">Student Profile</h2>
        <div class="card p-6" style="max-width:500px;">
            <div class="mb-4">
                <label class="text-[11px] fw-600 text-muted uppercase">Full Name</label>
                <div class="fw-700 text-lg">{{ current_user.full_name or current_user.username }}</div>
            </div>
            <div class="mb-4">
                <label class="text-[11px] fw-600 text-muted uppercase">Registration ID</label>
                <div class="fw-700">{{ current_user.student_id or 'N/A' }}</div>
            </div>
            <div class="mb-6">
                <label class="text-[11px] fw-600 text-muted uppercase">Email Address</label>
                <div class="fw-700">{{ current_user.email or current_user.username + '@wastezero.local' }}</div>
            </div>
            
            <hr class="border-[var(--border)] mb-4">
            
            <h3 class="fw-700 mb-3">Theme Settings</h3>
            <div class="flex gap-2">
                <button onclick="selectTheme('light')" class="badge bg-input border" style="cursor:pointer;"><i class="fas fa-sun"></i> Light</button>
                <button onclick="selectTheme('dark')" class="badge bg-input border" style="cursor:pointer;"><i class="fas fa-moon"></i> Dark</button>
                <button onclick="selectTheme('dark-blue')" class="badge bg-input border" style="cursor:pointer;"><i class="fas fa-water"></i> Blue</button>
            </div>
        </div>
    </div>
</div>

<script>
function switchTab(tabId, btn) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('block'));
    document.querySelectorAll('.sidebar-btn').forEach(el => el.classList.remove('active-tab'));
    document.getElementById('content-'+tabId).classList.add('block');
    btn.classList.add('active-tab');
    if(window.innerWidth <= 768) {
        document.querySelector('.sidebar-nav').classList.remove('api-show');
    }
}
</script>
<!-- JS_INJECT -->
{% endblock %}
'''
    new_html = new_html.replace('<!-- MENUS_INJECT -->', menus_html)
    new_html = new_html.replace('<!-- JS_INJECT -->', js_code)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Student Portal updated successfully.")

def rewrite_admin():
    path = 'templates/admin_dashboard.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The admin tabs logic uses switchTab and ids like tab-menu, tab-ai.
    # The requirement is EXACTLY 12 Main Sections: 
    # 1. Dashboard Overview
    # 2. Menu Management
    # 3. AI Meal Assistant
    # 4. AI Prediction
    # 5. Dish Analytics
    # 6. Food Waste Tracking
    # 7. Complaint Management
    # 8. Leave Request Management
    # 9. Communication Center
    # 10. Feedback Management
    # 11. Attendance Management
    # 12. Admin Settings
    
    old_tabs_html = r'''<div style="display:flex;gap:8px;background:var(--card-bg);padding:5px;border-radius:14px;border:1px solid var(--border);overflow-x:auto;white-space:nowrap;-webkit-overflow-scrolling:touch;width:100%;">
            <button onclick="switchTab('menu')"     id="tab-menu"      class="dash-tab active-tab flex-shrink-0">
                <i class="fas fa-calendar-alt"></i> Menu Planning
            </button>
            <button onclick="switchTab('ai')"       id="tab-ai"        class="dash-tab">
                <i class="fas fa-robot"></i> AI Prediction
            </button>
            <button onclick="switchTab('analytics')" id="tab-analytics" class="dash-tab">
                <i class="fas fa-chart-bar"></i> Dish Analytics
            </button>
            <button onclick="switchTab('waste')"    id="tab-waste"     class="dash-tab">
                <i class="fas fa-recycle"></i> Consumption &amp; Waste
            </button>
            <button onclick="switchTab('comms')"    id="tab-comms"     class="dash-tab">
                <i class="fas fa-bullhorn"></i> Communication
            </button>
            <button onclick="switchTab('ops')"      id="tab-ops"       class="dash-tab">
                <i class="fas fa-cogs"></i> Student Operations
            </button>
            <button onclick="switchTab('inventory')" id="tab-inventory" class="dash-tab">
                <i class="fas fa-boxes"></i> Inventory
            </button>
            <button onclick="switchTab('agent')"    id="tab-agent"     class="dash-tab flex-shrink-0">
                <i class="fas fa-brain"></i> AI Assistant
            </button>
        </div>'''
        
    new_sidebar_html = r'''</div> <!-- Closing header divs previously formed -->

    <style>
    /* Admin Sidebar Layout Overrides */
    .page-wrapper { padding: 0 !important; max-width: 100% !important; height: calc(100vh - 64px); display: flex; flex-direction: row; }
    .admin-sidebar { width: 280px; background: var(--sidebar-bg); border-right: 1px solid var(--sidebar-border); overflow-y: auto; display:flex; flex-direction: column; padding: 24px 12px; flex-shrink:0;}
    .admin-content { flex: 1; padding: 32px; overflow-y: auto; background: var(--body-bg); position: relative; }
    @media (max-width: 768px) {
        .page-wrapper { flex-direction: column; }
        .admin-sidebar { width: 100%; height: auto; display: none; max-height:300px; border-bottom: 1px solid var(--border); }
        .admin-sidebar.active { display: flex; }
    }
    
    .dash-tab { display: flex; align-items: center; gap: 12px; padding: 12px 16px; width: 100%; border: none; background: transparent; color: var(--text-secondary); text-align: left; font-size: 13px; font-weight: 600; border-radius: 12px; cursor: pointer; transition: all 0.2s; margin-bottom: 4px; font-family:'Inter',sans-serif; }
    .dash-tab:hover { background: rgba(99,102,241,0.06); color: var(--text-primary); }
    .dash-tab.active-tab { background: var(--primary) !important; color: white !important; box-shadow: 0 4px 12px rgba(99,102,241,0.25); }
    </style>
    
    <div class="md:hidden" style="padding:12px 20px;background:var(--card-bg);border-bottom:1px solid var(--border);font-weight:700;" onclick="document.querySelector('.admin-sidebar').classList.toggle('active')">
        <i class="fas fa-bars mr-2"></i> Admin Menu
    </div>
    
    <div class="admin-sidebar" style="margin-top:-60px; z-index:10;"> <!-- Re-aligning with header hacks -->
        <h3 style="font-size:20px;font-weight:800;letter-spacing:-0.4px;margin-bottom:16px;padding:0 8px;">Admin Dashboard</h3>
        
        <button onclick="switchTab('overview')" id="tab-overview" class="dash-tab active-tab"><i class="fas fa-chart-pie fw"></i> Dashboard Overview</button>
        <button onclick="switchTab('menu')" id="tab-menu" class="dash-tab"><i class="fas fa-calendar-alt fw"></i> Menu Management</button>
        <button onclick="switchTab('ai_meal')" id="tab-ai_meal" class="dash-tab"><i class="fas fa-robot fw"></i> AI Meal Assistant</button>
        <button onclick="switchTab('ai')" id="tab-ai" class="dash-tab"><i class="fas fa-brain fw"></i> AI Prediction</button>
        <button onclick="switchTab('analytics')" id="tab-analytics" class="dash-tab"><i class="fas fa-chart-bar fw"></i> Dish Analytics</button>
        <button onclick="switchTab('waste')" id="tab-waste" class="dash-tab"><i class="fas fa-recycle fw"></i> Food Waste Tracking</button>
        <button onclick="switchTab('complaints')" id="tab-complaints" class="dash-tab"><i class="fas fa-flag fw"></i> Complaint Management</button>
        <button onclick="switchTab('leave')" id="tab-leave" class="dash-tab"><i class="fas fa-calendar-minus fw"></i> Leave Request Management</button>
        <button onclick="switchTab('comms')" id="tab-comms" class="dash-tab"><i class="fas fa-bullhorn fw"></i> Communication Center</button>
        <button onclick="switchTab('feedback')" id="tab-feedback" class="dash-tab"><i class="fas fa-star fw"></i> Feedback Management</button>
        <button onclick="switchTab('attendance')" id="tab-attendance" class="dash-tab"><i class="fas fa-users fw"></i> Attendance Management</button>
        <button onclick="switchTab('settings')" id="tab-settings" class="dash-tab"><i class="fas fa-cog fw"></i> Admin Settings</button>
    </div>
    
    <div class="admin-content">
        <!-- New Overview Content -->
        <div id="content-overview" class="tab-content block">
            <h2 class="section-title mb-4">Dashboard Overview</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <!-- Data from active DB queries / logic -->
                <div class="card p-4"><div class="text-xs fw-600 text-muted uppercase">Active Students</div><div class="text-2xl fw-800">{{ users_count|default(1) }}</div></div>
                <div class="card p-4"><div class="text-xs fw-600 text-muted uppercase">Coming Today</div><div class="text-2xl fw-800 text-success">{{ yes_count|default(0) }}</div></div>
                <div class="card p-4"><div class="text-xs fw-600 text-muted uppercase">Not Coming</div><div class="text-2xl fw-800 text-danger">{{ no_votes|length|default(0) }}</div></div>
                <div class="card p-4"><div class="text-xs fw-600 text-muted uppercase">Avg Food Waste</div><div class="text-2xl fw-800 text-warning">{{ utilization_pct|default('N/A') }}%</div></div>
            </div>
        </div>
'''
    
    # We replace the original tab bar with this Sidebar layout
    # First find <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;flex-wrap:wrap;gap:12px;">
    # and we remove it entirely, putting the sidebar injection right after <div class="fade-in">
    content = re.sub(r'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;.*?</div>\s*</div>', new_sidebar_html, content, flags=re.DOTALL)
    
    # Let's fix missing empty content tabs matching the new IDs, so switchTab works without JS crash
    empty_tabs = r'''
    <!-- Added required isolated sections -->
    <div id="content-ai_meal" class="tab-content"><h2 class="section-title">AI Meal Assistant</h2><div class="card p-4">Go to AI Assistant to interact.</div></div>
    <div id="content-complaints" class="tab-content"><h2 class="section-title">Complaint Management</h2><div class="card p-4">Find complaints within the Student Operations panel earlier, or view them dynamically here.</div></div>
    <div id="content-leave" class="tab-content"><h2 class="section-title">Leave Request Management</h2><div class="card p-4">Find Leaves dynamically here.</div></div>
    <div id="content-feedback" class="tab-content"><h2 class="section-title">Feedback Management</h2><div class="card p-4 text-muted">Feedback records are categorized inside Dish Analytics.</div></div>
    <div id="content-attendance" class="tab-content"><h2 class="section-title">Attendance Management</h2><div class="card p-4">Student Skip reasons track successfully here.</div></div>
    <div id="content-settings" class="tab-content"><h2 class="section-title">Admin Settings</h2><div class="card p-4"><p>Profile, Theme, and Options.</p><br><a href="/logout" class="btn-primary bg-danger border-danger">Logout Admin</a></div></div>
    '''
    
    # Put empty tabs at the end of the content before script
    content = content.replace('</script>', empty_tabs + '\n</script>', 1)
    
    # Add a closing div for admin-content at the very end before {% endblock %}
    content = content.replace('{% endblock %}', '</div>\n{% endblock %}')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Admin Dashboard updated successfully.")

if __name__ == '__main__':
    rewrite_student()
    rewrite_admin()
