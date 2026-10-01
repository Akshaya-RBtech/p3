import os

print("Fixing Sidebar text...")

# Update Student Portal
sp = 'templates/student_portal.html'
with open(sp, 'r', encoding='utf-8') as f:
    s_html = f.read()

s_html = s_html.replace('1. Home Dashboard', 'Home Dashboard')
s_html = s_html.replace('2. Weekly Calendar', 'Weekly Meal Calendar')
s_html = s_html.replace('3. AI Assistant', 'Student AI Assistant')
s_html = s_html.replace('4. Notifications', 'Notifications')
s_html = s_html.replace('5. Food Feedback', 'Food Feedback')
s_html = s_html.replace('6. Complaints', 'Student Complaints')
s_html = s_html.replace('7. Leave Requests', 'Student Leave Requests')
s_html = s_html.replace('8. My Profile', 'Student Profile')
s_html = s_html.replace('9. Logout', 'Logout')

with open(sp, 'w', encoding='utf-8') as f:
    f.write(s_html)

# Update Admin Dashboard
ap = 'templates/admin_dashboard.html'
with open(ap, 'r', encoding='utf-8') as f:
    a_html = f.read()

a_html = a_html.replace('1. Dashboard Overview', 'Dashboard Overview')
a_html = a_html.replace('2. Menu Management', 'Menu Management')
a_html = a_html.replace('3. AI Meal Assistant', 'AI Meal Assistant')
a_html = a_html.replace('4. AI Prediction', 'AI Prediction')
a_html = a_html.replace('5. Dish Analytics', 'Dish Analytics')
a_html = a_html.replace('6. Food Waste Tracking', 'Food Waste Tracking')
a_html = a_html.replace('7. Complaint Mgmt', 'Complaint Management')
a_html = a_html.replace('8. Leave Request Mgmt', 'Leave Request Management')
a_html = a_html.replace('9. Communication Center', 'Communication Center')
a_html = a_html.replace('10. Feedback Mgmt', 'Feedback Management')
a_html = a_html.replace('11. Attendance Tracking', 'Attendance Management')
a_html = a_html.replace('12. Admin Settings', 'Admin Settings')

with open(ap, 'w', encoding='utf-8') as f:
    f.write(a_html)

print("Sidesbars Updated Successfully!")
