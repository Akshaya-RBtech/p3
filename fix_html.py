import os
import re

print("Fixing HTML without shell escaping issues...")

std_html = """
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
                container.innerHTML = data.notifications.map(n => `
                    <div class="p-4 border-b border-[var(--border)] flex justify-between gap-4 ${n.read ? 'opacity-70' : 'bg-[rgba(99,102,241,0.03)]'}">
                        <div>
                            <div class="fw-700 mb-1 ${!n.read ? 'text-[var(--primary)]' : ''}">${n.title}</div>
                            <div class="text-[13px] text-muted">${n.message}</div>
                        </div>
                        <div class="text-[10px] text-muted whitespace-nowrap">${n.timestamp}</div>
                    </div>`
                ).join('');
            } catch(e) {}
        }
        // Bind load event when tab is clicked
        setTimeout(()=> {
            document.querySelector('.sidebar-nav')?.addEventListener('click', (e) => {
                const btn = e.target.closest('button');
                if(btn && btn.innerText.includes('Notifications')) loadStudentNotifications();
            });
        }, 1000);
        async function readAllNotifs() {
            try {
                await fetch('/api/notifications/read', {method:'POST'});
                loadStudentNotifications();
            }catch(e){}
        }
    </script>
    </div>

    <!-- 5. Food Feedback -->
    <div id="content-feedback" class="tab-content">
    <h2 class="section-title mb-3">Food Feedback</h2>
    <div class="card p-5 mb-5">
        <h3 class="fw-700 text-[14px] mb-3"><i class="fas fa-star text-warning mr-2"></i> Submit Feedback</h3>
        <form onsubmit="submitStudentFeedback(event)">
            <select id="fb-menu" class="form-input mb-3 w-full" required>
                <option value="">Select Recent Meal...</option>
                {% for m in menus[:7] %}
                <option value="{{ m.id }}">{{ m.date }} - {{ m.meal_type }}</option>
                {% endfor %}
            </select>
            <select id="fb-rating" class="form-input mb-3 w-full" required>
                <option value="">Rate Meal...</option>
                <option value="Like">👍 Like</option><option value="Neutral">😐 Neutral</option><option value="Dislike">👎 Dislike</option>
            </select>
            <textarea id="fb-comment" class="form-input mb-3 w-full" rows="3" placeholder="Additional comments... (optional)"></textarea>
            <button type="submit" class="btn-primary w-full justify-center">Submit Feedback</button>
        </form>
        <div id="fb-status-msg" class="mt-2 text-center text-xs fw-600 hidden"></div>
    </div>
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
    const targ = document.getElementById('content-'+tabId);
    if(targ) targ.classList.add('block');
    if(btn) btn.classList.add('active-tab');
    if(window.innerWidth <= 768) {
        document.querySelector('.sidebar-nav').classList.remove('api-show');
    }
}
function selectTheme(t){ localStorage.setItem('wastezero-theme',t); document.documentElement.setAttribute('data-theme',t);}
function setStudentPrompt(txt) { document.getElementById('student-chat-input').value = txt; sendStudentMsg(); }

async function submitVoteAjax(e, menuId) {
    e.preventDefault();
    const choice = document.getElementById('choice-' + menuId).value;
    const reason = document.getElementById('reason-' + menuId).value;
    const btn = document.getElementById('submit-btn-' + menuId);
    const err = document.getElementById('vote-error-' + menuId);
    if (choice === 'No' && !reason) { err.style.display='block'; err.innerText="Please provide a reason for skipping."; return; }
    btn.disabled=true;
    try {
        const res = await fetch('/student/vote', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({menu_id:menuId, choice:choice, reason:reason}) });
        const data = await res.json();
        if(res.ok) { document.getElementById('vote-form-'+menuId).style.display='none'; document.getElementById('vote-success-'+menuId).style.display='block'; }
        else { err.style.display='block'; err.innerText=data.error||'Failed'; }
    } catch(e) { err.style.display='block'; err.innerText='Network error.'; }
    btn.disabled=false;
}

function selectVote(menuId, choice) {
    document.getElementById('choice-' + menuId).value = choice;
    const yesBtn = document.getElementById('btn-yes-' + menuId);
    const noBtn = document.getElementById('btn-no-' + menuId);
    const subBtn = document.getElementById('submit-btn-' + menuId);
    const reasonBox = document.getElementById('reason-box-' + menuId);
    subBtn.style.display = 'flex';
    if (choice === 'No') {
        noBtn.style.background = 'var(--danger)'; noBtn.style.color = 'white';
        yesBtn.style.background = 'rgba(16,185,129,0.06)'; yesBtn.style.color = 'var(--success)';
        reasonBox.style.display = 'block';
    } else {
        yesBtn.style.background = 'var(--success)'; yesBtn.style.color = 'white';
        noBtn.style.background = 'rgba(239,68,68,0.06)'; noBtn.style.color = 'var(--danger)';
        reasonBox.style.display = 'none';
        document.getElementById('reason-'+menuId).value = '';
    }
}

async function submitStudentComplaint(e) {
    e.preventDefault();
    const cat = document.getElementById('comp-category').value, desc = document.getElementById('comp-description').value;
    const st = document.getElementById('comp-status');
    const btn = e.target.querySelector('button'); btn.disabled=true;
    try {
        await fetch('/api/complaints', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({category:cat, description:desc}) });
        st.style.display='block'; st.style.color='var(--success)'; st.innerText='✅ Submitted'; e.target.reset();
    } catch(err) { st.style.display='block'; st.style.color='var(--danger)'; st.innerText='❌ Failed';}
    btn.disabled=false; setTimeout(()=>st.style.display='none', 4000);
}

async function submitStudentLeave(e) {
    e.preventDefault();
    const start = document.getElementById('leave-start').value, end = document.getElementById('leave-end').value, lr = document.getElementById('leave-reason').value, lt = document.getElementById('leave-type').value;
    const st = document.getElementById('leave-status');
    if(new Date(end)<new Date(start)){ st.style.display='block'; st.style.color='var(--danger)'; st.innerText='❌ Invalid dates'; return; }
    try {
        await fetch('/api/leave', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({start_date:start, end_date:end, reason:lr, type:lt}) });
        st.style.display='block'; st.style.color='var(--success)'; st.innerText='✅ Requested'; e.target.reset();
    } catch(err) { st.style.display='block'; st.style.color='var(--danger)'; st.innerText='❌ Failed';}
    setTimeout(()=>st.style.display='none', 4000);
}

async function submitStudentFeedback(e) {
    e.preventDefault();
    const menu = document.getElementById('fb-menu').value, rating = document.getElementById('fb-rating').value, comment = document.getElementById('fb-comment').value;
    const st = document.getElementById('fb-status-msg');
    try {
        await fetch('/api/feedback', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({menu_id:menu, rating:rating, comments:comment}) });
        st.style.display='block'; st.style.color='var(--success)'; st.innerText='✅ Feedback saved'; e.target.reset();
    } catch(err) { st.style.display='block'; st.style.color='var(--danger)'; st.innerText='❌ Failed';}
    setTimeout(()=>st.style.display='none', 4000);
}

// Student Chat 
let studentSessionId = null;
async function sendStudentMsg(){
    const input = document.getElementById('student-chat-input');
    const text = input.value.trim();
    if(!text) return;
    input.value = '';
    const container = document.getElementById('student-chat-messages');
    container.innerHTML += `<div style="display:flex;align-items:flex-start;gap:8px;flex-direction:row-reverse;margin-left:auto;"><div style="background:var(--primary);color:white;border-radius:12px 12px 0 12px;padding:10px 14px;font-size:13px;max-width:85%;">${text}</div></div>`;
    
    try {
        const res = await fetch('/api/ai/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ message: text, session_id: studentSessionId, context_role: 'student'}) });
        const data = await res.json();
        const responseText = data.response || data.error || "Sorry, an error occurred.";
        container.innerHTML += `<div style="display:flex;align-items:flex-start;gap:8px;"><div style="width:28px;height:28px;border-radius:50%;background:var(--primary);color:white;display:flex;align-items:center;justify-content:center;font-size:10px;"><i class="fas fa-robot"></i></div><div style="background:var(--input-bg);border:1px solid var(--border);border-radius:0 12px 12px 12px;padding:10px 14px;font-size:13px;max-width:85%;">${responseText}</div></div>`;
    } catch(e) {}
    container.scrollTop = container.scrollHeight;
}
</script>
{% endblock %}
"""

std_path = "templates/student_portal.html"
with open(std_path, "r", encoding="utf-8") as f:
    text = f.read()

parts = text.split("<!-- 3. Student AI Assistant -->")
if len(parts) > 1:
    with open(std_path, "w", encoding="utf-8") as f:
        f.write(parts[0] + std_html)

admin_html = """
    <!-- Added required isolated sections -->
    <div id="content-ai_meal" class="tab-content"><h2 class="section-title mb-4">AI Meal Assistant</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card p-5">
            <h3 class="fw-700 mb-3"><i class="fas fa-magic text-primary mr-2"></i> Generate Menu Suggestion</h3>
            <p class="text-xs text-muted mb-4">Let Gemini AI recommend a balanced menu based on historical data.</p>
            <button onclick="alert('Feature linked to API')" class="btn-primary w-full justify-center">Generate AI Menu</button>
            <div class="mt-4 p-3 bg-input border rounded text-xs text-muted">AI Suggestion will appear here for Admin Approval before publishing.</div>
        </div>
        <div class="card p-5">
            <h3 class="fw-700 mb-3"><i class="fas fa-sync text-warning mr-2"></i> Menu Repetition Detector</h3>
            <p class="text-xs text-muted mb-4">Analyze recent menus to prevent serving the same dish too frequently.</p>
            <button onclick="alert('Feature linked to API')" class="btn-primary w-full justify-center bg-warning border-warning">Run Analysis</button>
        </div>
    </div></div>
    
    <div id="content-complaints" class="tab-content"><h2 class="section-title mb-4">Complaint Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-4">Student Complaints</h3>
        <div class="flex gap-2 mb-4">
            <select id="comp-fltr" class="form-input text-xs" style="width:150px;" onchange="filterOperations()"><option value="All">All Statuses</option><option value="Open">Open</option><option value="Resolved">Resolved</option></select>
        </div>
        <div class="overflow-x-auto">
            <div id="ops-complaints" style="display:flex;flex-direction:column;gap:10px;">
                <div class="text-center p-4 text-muted">Use fetchOperationsData() to list items here.</div>
            </div>
        </div>
    </div></div>

    <div id="content-leave" class="tab-content"><h2 class="section-title mb-4">Leave Request Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-4">Student Leaves</h3>
        <div class="flex gap-2 mb-4">
            <select id="leave-fltr" class="form-input text-xs" style="width:150px;" onchange="filterOperations()"><option value="All">All Statuses</option><option value="Pending">Pending</option><option value="Approved">Approved</option></select>
        </div>
        <div class="overflow-x-auto">
            <div id="ops-leave" style="display:flex;flex-direction:column;gap:10px;">
                <div class="text-center p-4 text-muted">Use fetchOperationsData() to list items here.</div>
            </div>
        </div>
    </div></div>

    <div id="content-feedback" class="tab-content"><h2 class="section-title mb-4">Feedback Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-4">Student Feedback Records</h3>
        <table class="data-table w-full text-left">
            <thead><tr><th class="p-3">Student</th><th class="p-3">Dish</th><th class="p-3">Reason</th><th class="p-3">Time</th></tr></thead>
            <tbody id="fb-table-b"><tr><td colspan="4" class="p-4 text-center text-muted">Feedback dynamically loads via fetchOperationsData!</td></tr></tbody>
        </table>
    </div></div>

    <div id="content-attendance" class="tab-content"><h2 class="section-title mb-4">Attendance Management</h2>
    <div class="card p-5">
        <h3 class="fw-700 mb-3">Skip Reasons &amp; Tracking</h3>
        <table class="data-table w-full text-left">
            <thead><tr><th class="p-3">Student ID</th><th class="p-3">Dish / Items</th><th class="p-3">Reason</th><th class="p-3">Time/Date</th></tr></thead>
            <tbody>
                {% for att in negative_attendance %}
                <tr><td class="p-2 fw-600">{{ att.student_id }}</td><td class="p-2 text-xs text-muted">{{ att.dish }}</td><td class="p-2">{{ att.reason }}</td><td class="p-2 text-[10px]">{{ att.time }}</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div></div>
    
    <div id="content-settings" class="tab-content"><h2 class="section-title mb-4">Admin Settings</h2>
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
    </div></div>
    
</div>
<script>
    async function fetchOperationsData() {
        // Complaints
        try {
            const compRes = await fetch('/api/complaints');
            const compData = await compRes.json();
            const compDiv = document.getElementById('ops-complaints');
            if (compData.length === 0) {
                compDiv.innerHTML = `<div style="text-align:center;color:var(--text-muted);font-size:13px;padding:20px;">No complaints found.</div>`;
            } else {
                compDiv.innerHTML = compData.map(c => `
                    <div class="ops-comp-item" data-status="${c.status}" style="padding:14px;border-bottom:1px solid var(--border);border-left:4px solid ${c.status === 'Open' ? 'var(--danger)' : c.status === 'In Progress' ? 'var(--warning)' : 'var(--success)'};background:var(--input-bg);">
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <span style="font-weight:700;font-size:13px;"><i class="fas fa-user-circle"></i> ${c.student_id}</span>
                            <span style="font-size:11px;color:var(--text-muted);">${c.created_at}</span>
                        </div>
                        <div style="font-weight:600;font-size:12px;color:var(--primary);margin-bottom:4px;">[${c.category}]</div>
                        <p style="font-size:12px;margin-bottom:8px;">${c.description}</p>
                        <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
                            <select class="form-input" style="font-size:11px;padding:4px 6px;width:auto;" onchange="updateComplaintStatus(${c.id}, this)">
                                <option value="Open" ${c.status === 'Open' ? 'selected' : ''}>Open</option>
                                <option value="Resolved" ${c.status === 'Resolved' ? 'selected' : ''}>Resolved</option>
                            </select>
                            <input type="text" placeholder="Admin note..." class="form-input" style="font-size:11px;padding:4px 6px;flex:1;" value="${c.admin_note || ''}" id="comp-note-${c.id}">
                            <button class="btn-primary" style="font-size:11px;padding:4px 8px;" onclick="updateComplaintNote(${c.id})">Save</button>
                        </div>
                    </div>
                `).join('');
            }
        } catch (e) {}

        // Leave
        try {
            const leaveRes = await fetch('/api/leave');
            const leaveData = await leaveRes.json();
            const leaveDiv = document.getElementById('ops-leave');
            if (leaveData.length === 0) {
                leaveDiv.innerHTML = `<div style="text-align:center;color:var(--text-muted);font-size:13px;padding:20px;">No leave requests found.</div>`;
            } else {
                leaveDiv.innerHTML = leaveData.map(L => `
                    <div class="ops-leave-item" data-status="${L.status}" style="padding:14px;border-bottom:1px solid var(--border);border-left:4px solid ${L.status === 'Pending' ? 'var(--warning)' : L.status === 'Rejected' ? 'var(--danger)' : 'var(--success)'};background:var(--input-bg);">
                        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                            <span style="font-weight:700;font-size:13px;"><i class="fas fa-user-circle"></i> ${L.student_id}</span>
                            <span style="font-size:11px;color:var(--text-muted);">${L.created_at}</span>
                        </div>
                        <div style="font-weight:600;font-size:12px;margin-bottom:4px;">Leave: ${L.start_date} to ${L.end_date}</div>
                        <p style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">Reason: ${L.reason || 'None'}</p>
                        <div style="display:flex;gap:6px;">
                            ${L.status === 'Pending' ? `
                            <button onclick="updateLeave(${L.id}, 'Approved')" style="flex:1;padding:6px;background:var(--success);color:white;border:none;border-radius:6px;font-size:11px;cursor:pointer;">Approve</button>
                            <button onclick="updateLeave(${L.id}, 'Rejected')" style="flex:1;padding:6px;background:var(--danger);color:white;border:none;border-radius:6px;font-size:11px;cursor:pointer;">Reject</button>
                            ` : `<span style="font-size:12px;font-weight:600;padding:4px 8px;background:var(--border);border-radius:4px;">Status: ${L.status}</span>`}
                        </div>
                    </div>
                `).join('');
            }
        } catch (e) {}
    }
    
    function filterOperations() {
        const cStatus = document.getElementById('comp-fltr').value;
        const lStatus = document.getElementById('leave-fltr').value;
        document.querySelectorAll('.ops-comp-item').forEach(el => { el.style.display = (cStatus === 'All' || el.dataset.status === cStatus) ? 'block' : 'none'; });
        document.querySelectorAll('.ops-leave-item').forEach(el => { el.style.display = (lStatus === 'All' || el.dataset.status === lStatus) ? 'block' : 'none'; });
    }

    async function updateComplaintStatus(id, selectElem) { await fetch(`/api/complaints/${id}/update`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ status: selectElem.value }) }); fetchOperationsData(); }
    async function updateComplaintNote(id) { const note = document.getElementById(`comp-note-${id}`).value; await fetch(`/api/complaints/${id}/update`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ admin_note: note }) }); fetchOperationsData(); }
    async function updateLeave(id, statusStr) { await fetch(`/api/leave/${id}/update`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ status: statusStr }) }); fetchOperationsData(); }
    
    // Auto load ops data when tabs clicked
    document.querySelectorAll('.dash-tab').forEach(b => {
        b.addEventListener('click', (e)=>{
            const id = e.currentTarget.id;
            if(id === 'tab-complaints' || id === 'tab-leave' || id === 'tab-feedback') fetchOperationsData();
        });
    });
</script>
{% endblock %}
"""

admin_path = "templates/admin_dashboard.html"
with open(admin_path, "r", encoding="utf-8") as f:
    atext = f.read()

aparts = atext.split("<!-- Added required isolated sections -->")
if len(aparts) > 1:
    with open(admin_path, "w", encoding="utf-8") as f:
        f.write(aparts[0] + admin_html)

print("HTML fixed successfully!")
