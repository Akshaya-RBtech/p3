import re

def fix_student_html():
    with open('templates/student_portal.html', encoding='utf-8') as f:
        html = f.read()

    # The broken part is at content-home
    broken_str = '''    <!-- ===== HOME TAB ===== -->
    <div id="content-home" class="tab-content block" style="margin-top:24px;">
                </div>
            </div>

            <!-- Card Body -->
            <div style="padding:18px 20px;">
                <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Dishes 🍽️</div>
                <p style="font-size:14px;font-weight:600;color:var(--text-primary);line-height:1.5;margin-bottom:18px;">{{ menu.items }}</p>'''

    fixed_str = '''    <!-- ===== HOME TAB ===== -->
    <div id="content-home" class="tab-content block" style="margin-top:24px;">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="col-span-1 lg:col-span-2" style="display:flex;flex-direction:column;gap:16px;">
                {% for menu in menus %}
                <div class="card" style="background:#fff;border-radius:16px;box-shadow:0 10px 40px rgba(0,0,0,0.05);overflow:hidden;border:1px solid var(--border);">
                    <!-- Card Body -->
                    <div style="padding:18px 20px;">
                        <div style="font-size:11px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;">Dishes 🍽️</div>
                        <p style="font-size:14px;font-weight:600;color:var(--text-primary);line-height:1.5;margin-bottom:18px;">{{ menu.items }}</p>'''
    
    if '{% for menu in menus %}' not in broken_str and broken_str in html:
        html = html.replace(broken_str, fixed_str)
        with open('templates/student_portal.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Fixed 500 error loop in student portal.")
    else:
        print("Loop already looks fixed or string not found.")
        
def add_logout_if_missing():
    with open('app.py', encoding='utf-8') as f:
        html = f.read()
    if '@app.route(\'/logout\')' not in html:
        logout_code = '''
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
'''
        # Read the file and insert it before the last app.run() or somewhere safe.
        html += logout_code
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Added logout route to app.py")
    else:
        print("Logout route already exists.")
        
fix_student_html()
add_logout_if_missing()
