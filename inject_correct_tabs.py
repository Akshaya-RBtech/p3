import re

def fix_student():
    path = 'templates/student_portal.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 2. WEEKLY MEAL CALENDAR 
    calendar_html = r'''
    <h2 class="section-title mb-3">Weekly Meal Calendar</h2>
    <div class="card p-5 mb-5 overflow-x-auto">
        <table class="data-table w-full text-left" style="min-width:600px;">
            <thead><tr><th class="p-3 border-b border-[var(--border)]">Date</th><th class="p-3 border-b border-[var(--border)]">Meal</th><th class="p-3 border-b border-[var(--border)]">Dishes</th></tr></thead>
            <tbody>
                {% for m in menus %}
                <tr class="border-b border-[var(--border)]">
                    <td class="p-3 fw-600">{{ m.date }}</td>
                    <td class="p-3"><span class="badge badge-primary">{{ m.meal_type }}</span></td>
                    <td class="p-3 text-muted">{{ m.items }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <h3 class="section-title mb-3 text-lg">Attendance History</h3>
    <div class="card p-5 overflow-x-auto">
        <table class="data-table w-full text-left" style="min-width:600px;">
            <thead><tr><th class="p-3 border-b border-[var(--border)]">Menu ID</th><th class="p-3 border-b border-[var(--border)]">Your Vote</th></tr></thead>
            <tbody>
                {% if voted_ids %}
                    {% for v_id in voted_ids %}
                    <tr class="border-b border-[var(--border)]">
                        <td class="p-3">Menu #{{ v_id }}</td>
                        <td class="p-3"><span class="badge badge-success">Confirmed</span></td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="2" class="p-4 text-center text-muted">No attendance recorded yet.</td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
    '''

    # 4. NOTIFICATIONS
    notif_html = r'''
    <div class="flex justify-between items-center mb-5">
        <h2 class="section-title">Notifications</h2>
        <button onclick="readAllNotifs()" class="btn-primary text-xs">Mark All Read</button>
    </div>
    <div class="card p-5" id="full-notif-list" style="max-height:500px; overflow-y:auto;">
        <div class="text-center p-4 text-muted" id="notif-loading"><i class="fas fa-spinner fa-spin mr-2"></i> Loading notifications...</div>
    </div>
    <script>
        async function loadStudentNotifications() {
            try {
                const res = await fetch('/api/notifications');
                const data = await res.json();
                const container = document.getElementById('full-notif-list');
                if(!data.notifications || data.notifications.length === 0) {
                    container.innerHTML = '<div class="text-center p-4 text-muted">No notifications found.</div>';
                    return;
                }
                container.innerHTML = data.notifications.map(n => 
                    <div class="p-4 border-b border-[var(--border)] flex justify-between gap-4 ">
                        <div>
                            <div class="fw-700 mb-1 "></div>
                            <div class="text-[13px] text-muted"></div>
                        </div>
                        <div class="text-[10px] text-muted whitespace-nowrap"></div>
                    </div>
                ).join('');
            } catch(e) {}
        }
        // Bind load event when tab is clicked
        setTimeout(()=> {
            const btn = document.querySelector('button[onclick="switchTab(\\\'notifications\\\', this)"]');
            if(btn) btn.addEventListener('click', loadStudentNotifications);
        }, 1000);
    </script>
    '''

    # 5. FOOD FEEDBACK
    feedback_html = r'''
    <h2 class="section-title mb-3">Food Feedback</h2>
    <div class="card p-5 mb-5">
        <h3 class="fw-700 text-[14px] mb-3"><i class="fas fa-star text-warning mr-2"></i> Submit Feedback</h3>
        <p class="text-xs text-muted mb-4">You can post feedback directly from the Home Dashboard after confirming you attended a meal.</p>
    </div>
    <div class="card p-5">
        <h3 class="fw-700 text-[14px] mb-3">Feedback History</h3>
        <div class="text-center p-4 text-muted text-xs">Your previous feedback is accessible here. (Currently loaded dynamically on Home tab)</div>
    </div>
    '''

    # Replace placeholders
    html = re.sub(r'<div id="content-calendar" class="tab-content">.*?</div>\s*<!-- 3\.', f'<div id="content-calendar" class="tab-content">{calendar_html}</div>\n    <!-- 3.', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-notifications" class="tab-content">.*?</div>\s*<!-- 5\.', f'<div id="content-notifications" class="tab-content">{notif_html}</div>\n    <!-- 5.', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-feedback" class="tab-content">.*?</div>\s*<!-- 6\.', f'<div id="content-feedback" class="tab-content">{feedback_html}</div>\n    <!-- 6.', html, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

def fix_admin():
    path = 'templates/admin_dashboard.html'
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Define actual content for the empty admin tabs
    
    # 3. AI Meal Assistant
    ai_meal_html = r'''<h2 class="section-title mb-4">AI Meal Assistant</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card p-5">
            <h3 class="fw-700 mb-3"><i class="fas fa-magic text-primary mr-2"></i> Generate Menu Suggestion</h3>
            <p class="text-xs text-muted mb-4">Let Gemini AI recommend a balanced menu based on historical data.</p>
            <button class="btn-primary w-full justify-center">Generate AI Menu</button>
            <div class="mt-4 p-3 bg-input border rounded text-xs text-muted">AI Suggestion will appear here for Admin Approval before publishing.</div>
        </div>
        <div class="card p-5">
            <h3 class="fw-700 mb-3"><i class="fas fa-sync text-warning mr-2"></i> Menu Repetition Detector</h3>
            <p class="text-xs text-muted mb-4">Analyze recent menus to prevent serving the same dish too frequently.</p>
            <button class="btn-primary w-full justify-center bg-warning border-warning">Run Analysis</button>
        </div>
    </div>'''

    # 7. Complaint Management
    complaints_html = r'''<h2 class="section-title mb-4">Complaint Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-4">Student Complaints</h3>
        <div class="flex gap-2 mb-4">
            <select class="form-input text-xs" style="width:150px;"><option>All Statuses</option><option>Pending</option><option>Resolved</option></select>
            <select class="form-input text-xs" style="width:150px;"><option>All Categories</option></select>
        </div>
        <div class="overflow-x-auto">
            <table class="data-table w-full text-left">
                <thead><tr><th class="p-3">Category</th><th class="p-3">Description</th><th class="p-3">Status</th><th class="p-3">Action</th></tr></thead>
                <tbody>
                    <tr><td colspan="4" class="p-4 text-center text-muted">Complaints loop will safely populate here. Use ops panel if merging.</td></tr>
                </tbody>
            </table>
        </div>
    </div>'''

    # 8. Leave Request Management
    leave_html = r'''<h2 class="section-title mb-4">Leave Request Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-4">Student Leaves</h3>
        <div class="overflow-x-auto">
            <table class="data-table w-full text-left">
                <thead><tr><th class="p-3">Dates</th><th class="p-3">Type</th><th class="p-3">Reason</th><th class="p-3">Status</th><th class="p-3">Action</th></tr></thead>
                <tbody>
                    <tr><td colspan="5" class="p-4 text-center text-muted">Active leave requests populate here.</td></tr>
                </tbody>
            </table>
        </div>
    </div>'''

    # 10. Feedback Management
    feedback_html = r'''<h2 class="section-title mb-4">Feedback Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-4">Student Feedback Records</h3>
        <table class="data-table w-full text-left">
            <thead><tr><th class="p-3">Dish / Menu</th><th class="p-3">Rating</th><th class="p-3">Comment</th></tr></thead>
            <tbody><tr><td colspan="3" class="p-4 text-center text-muted">Feedback dynamically integrates into Dish Analytics charts.</td></tr></tbody>
        </table>
    </div>'''

    # 11. Attendance Management
    attendance_html = r'''<h2 class="section-title mb-4">Attendance Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-3">Skip Reasons &amp; Tracking</h3>
        <table class="data-table w-full text-left">
            <thead><tr><th class="p-3">Student Vote</th><th class="p-3">Reason</th><th class="p-3">Custom Reason</th></tr></thead>
            <tbody><tr><td colspan="3" class="p-4 text-center text-muted">Attendance NO reasoning logs appear here.</td></tr></tbody>
        </table>
    </div>'''

    # 12. Admin Settings
    settings_html = r'''<h2 class="section-title mb-4">Admin Settings</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card p-5">
            <h3 class="fw-700 mb-4 uppercase text-muted text-xs">Profile Details</h3>
            <div class="mb-3"><div class="fw-600 text-[11px] uppercase text-[var(--primary)]">Username</div><div class="fw-700">{{ current_user.username }}</div></div>
            <div class="mb-3"><div class="fw-600 text-[11px] uppercase text-[var(--primary)]">Role</div><div class="badge badge-primary">Administrator</div></div>
            <hr class="border-[var(--border)] my-4">
            <h3 class="fw-700 mb-3 uppercase text-muted text-xs">Theme Settings</h3>
            <div class="flex gap-2">
                <button onclick="changeTheme('light')" class="badge bg-input border" style="cursor:pointer;"><i class="fas fa-sun"></i> Light</button>
                <button onclick="changeTheme('dark')" class="badge bg-input border" style="cursor:pointer;"><i class="fas fa-moon"></i> Dark</button>
                <button onclick="changeTheme('dark-blue')" class="badge bg-input border" style="cursor:pointer;"><i class="fas fa-water"></i> Blue</button>
            </div>
        </div>
        <div class="card p-5 bg-[rgba(239,68,68,0.05)] border-[rgba(239,68,68,0.2)]">
            <h3 class="fw-700 mb-3 text-danger"><i class="fas fa-lock mr-2"></i> Secure Logout</h3>
            <p class="text-xs text-muted mb-4">End your secure administration session and clear tokens.</p>
            <a href="/logout" class="btn-primary w-full justify-center bg-danger border-danger hover:bg-red-600" style="text-decoration:none;">Logout Now</a>
        </div>
    </div>'''

    # Replace placeholders
    html = re.sub(r'<div id="content-ai_meal" class="tab-content">.*?</div>', f'<div id="content-ai_meal" class="tab-content">{ai_meal_html}</div>', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-complaints" class="tab-content">.*?</div>', f'<div id="content-complaints" class="tab-content">{complaints_html}</div>', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-leave" class="tab-content">.*?</div>', f'<div id="content-leave" class="tab-content">{leave_html}</div>', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-feedback" class="tab-content">.*?</div>', f'<div id="content-feedback" class="tab-content">{feedback_html}</div>', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-attendance" class="tab-content">.*?</div>', f'<div id="content-attendance" class="tab-content">{attendance_html}</div>', html, flags=re.DOTALL)
    html = re.sub(r'<div id="content-settings" class="tab-content">.*?</div>', f'<div id="content-settings" class="tab-content">{settings_html}</div>', html, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    fix_student()
    fix_admin()
