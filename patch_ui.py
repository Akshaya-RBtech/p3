import sys

# STUDENT
with open('templates/student_portal.html', 'r', encoding='utf-8') as f:
    s = f.read()

s_comp_rep = """<div class="card p-5 flex flex-col h-full">
                    <h3 class="fw-700 mb-4"><i class="fas fa-history mr-2 text-primary"></i> Complaint History</h3>
                    <div id="stu-comp-list" class="flex-1 flex flex-col gap-3 overflow-y-auto max-h-[300px]">
                        <div class="text-center text-sm text-muted p-4"><i class="fas fa-spinner fa-spin mr-2"></i> Loading history...</div>
                    </div>
                </div>"""

s = s.replace("""<div class="card p-5 flex flex-col h-full opacity-70">
                    <h3 class="fw-700 mb-4 text-muted"><i class="fas fa-history mr-2"></i> Complaint History</h3>
                    <div class="flex-1 flex items-center justify-center border-2 border-dashed border-[var(--border)] rounded-lg">
                        <div class="text-center text-sm text-muted p-4">
                            History is available via Admin console for MVP.<br>
                            Your submitted complaints are logged safely!
                        </div>
                    </div>
                </div>""", s_comp_rep)

s_leave_rep = """<div class="card p-5 flex flex-col h-full">
                    <h3 class="fw-700 mb-4"><i class="fas fa-history mr-2 text-warning"></i> Leave History</h3>
                    <div id="stu-leave-list" class="flex-1 flex flex-col gap-2 overflow-y-auto max-h-[300px]">
                        <div class="text-center text-sm text-muted p-4"><i class="fas fa-spinner fa-spin mr-2"></i> Loading history...</div>
                    </div>
                </div>"""

if 'id="stu-leave-list"' not in s:
    s = s.replace("""<div id="leave-status" class="mt-3 text-center text-xs fw-600 hidden"></div>
                </div>
            </div>
        </div>""", """<div id="leave-status" class="mt-3 text-center text-xs fw-600 hidden"></div>
                </div>
                """ + s_leave_rep + """
            </div>
        </div>""")

s_js = """
async function loadStudentHistory() {
    try {
        const cRes = await fetch('/api/complaints');
        const cData = await cRes.json();
        const cDiv = document.getElementById('stu-comp-list');
        if(cDiv && cData.length===0) cDiv.innerHTML='<div class="text-muted text-[11px] p-3 text-center">No complaints filed.</div>';
        else if(cDiv) cDiv.innerHTML = cData.map(c => `<div class="bg-[var(--input-bg)] border border-[var(--border)] p-3 rounded"><div class="flex justify-between items-center"><span class="fw-700 text-[11px] text-primary">${c.category}</span><span class="badge ${c.status==='Resolved'?'badge-success':c.status==='Open'?'badge-danger':'badge-warning'} text-[10px]">${c.status}</span></div><div class="text-[11px] mt-2 mb-2">${c.description}</div>${c.admin_note ? `<div class="text-[10px] text-muted border-t pt-1 border-[var(--border)]"><i class="fas fa-reply mr-1"></i> ${c.admin_note}</div>` : ''}</div>`).join('');
    } catch(e){}
    try {
        const lRes = await fetch('/api/leave');
        const lData = await lRes.json();
        const lDiv = document.getElementById('stu-leave-list');
        if(lDiv && lData.length===0) lDiv.innerHTML='<div class="text-muted text-[11px] p-3 text-center">No leave requests found.</div>';
        else if(lDiv) lDiv.innerHTML = lData.map(l => `<div class="bg-[var(--input-bg)] border border-[var(--border)] p-3 rounded"><div class="flex justify-between items-center"><span class="fw-700 text-[11px] text-primary">${l.start_date} to ${l.end_date}</span><span class="badge ${l.status==='Approved'?'badge-success':l.status==='Rejected'?'badge-danger':'badge-warning'} text-[10px]">${l.status}</span></div><div class="text-[11px] mt-1 text-muted">Reason: ${l.reason||'None'}</div></div>`).join('');
    } catch(e){}
}
"""

if 'loadStudentHistory()' not in s:
    s = s.replace('// Initialize home tab on load', s_js + '\n// Initialize home tab on load')
    s = s.replace('loadStudentNotifications();\n});', 'loadStudentNotifications();\n    loadStudentHistory();\n});')
    
    # And bind it to the tabs so clicking 'Complaints' re-fetches
    s = s.replace("if (tabId === 'notifications') {", "if (tabId === 'notifications' || tabId === 'complaints' || tabId === 'leave') {\n        loadStudentHistory();\n    }\n    if (tabId === 'notifications') {")

with open('templates/student_portal.html', 'w', encoding='utf-8') as f:
    f.write(s)

# ADMIN
with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
    a = f.read()

a_fb_js = """        // Feedback Form
        try {
            const fbRes = await fetch('/api/feedback');
            const fbData = await fbRes.json();
            const fbTable = document.getElementById('ops-feedback');
            if (fbTable) {
                if (fbData.length === 0) fbTable.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-muted">No feedback recorded.</td></tr>`;
                else fbTable.innerHTML = fbData.map(fb => `<tr class="border-b border-[var(--border)]"><td class="p-3 fw-600 text-[12px]"><i class="fas fa-user-circle text-muted mr-1"></i> ${fb.student_id}</td><td class="p-3 text-[12px]"><div class="fw-600 text-primary">${fb.dish}</div><div class="text-[10px] text-muted">${fb.meal} | ${fb.date}</div></td><td class="p-3"><span class="badge ${fb.rating === 'Excellent' || fb.rating === 'Like' || fb.rating === 'Good' ? 'badge-success' : fb.rating === 'Dislike' || fb.rating === 'Terrible' || fb.rating === 'Poor' ? 'badge-danger' : 'badge-warning'} text-[11px]">${fb.rating}</span><div class="text-[11px] mt-1 text-muted">${fb.comments||'No comment'}</div></td><td class="text-[10px] text-muted p-3">${fb.timestamp}</td></tr>`).join('');
            }
        }catch(e){}"""

a = a.replace("""        // Feedback Form
        try {
            const fbTable = document.getElementById('ops-feedback');
            // Assuming no dedicated feedback json endpoint, this requires just reloading if it's templated or leaving it.
            // MVP template loads the layout correctly. 
            if(fbTable && fbTable.innerHTML.includes('Mapping feedback')) {
                fbTable.innerHTML = `<tr><td colspan="4" class="p-6 text-center text-muted">Feedback logs loaded securely! Connect Database Endpoint to view real-time streams.</td></tr>`;
            }
        }catch(e){}""", a_fb_js)

with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(a)

print("UI Patched successfully!")
