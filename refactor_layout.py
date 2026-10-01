import re

with open('templates/layout.html', encoding='utf-8') as f:
    text = f.read()

# Replace Admin Drawer links
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-chart-pie"></i> Dashboard</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=dashboard" class="drawer-link"><i class="fas fa-chart-pie"></i> Dashboard</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-utensils"></i> Menu Management</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=menu" class="drawer-link"><i class="fas fa-utensils"></i> Menu Management</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-calendar-week"></i> Weekly Meal Calendar</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=weekly" class="drawer-link"><i class="fas fa-calendar-week"></i> Weekly Meal Calendar</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-users-viewfinder"></i> Attendance Tracker</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=attendance" class="drawer-link"><i class="fas fa-users-viewfinder"></i> Attendance Tracker</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-brain"></i> AI Meal Assistant</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=aimenu" class="drawer-link"><i class="fas fa-brain"></i> AI Meal Assistant</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-recycle"></i> Menu Repetition Detector</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=ai" class="drawer-link"><i class="fas fa-recycle"></i> Menu Repetition Detector</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-chart-line"></i> Dish Analytics</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=analytics" class="drawer-link"><i class="fas fa-chart-line"></i> Dish Analytics</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-leaf"></i> Food Waste Tracking</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=waste" class="drawer-link"><i class="fas fa-leaf"></i> Food Waste Tracking</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-box"></i> Inventory Stock</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=inventory" class="drawer-link"><i class="fas fa-box"></i> Inventory Stock</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-envelope-open-text"></i> Leave Requests</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=leave" class="drawer-link"><i class="fas fa-envelope-open-text"></i> Leave Requests</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-exclamation-triangle"></i> Complaints</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=complaints" class="drawer-link"><i class="fas fa-exclamation-triangle"></i> Complaints</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'admin_dashboard\') }}" class="drawer-link"><i class="fas fa-bullhorn"></i> Communications</a>',
    '<a href="{{ url_for(\'admin_dashboard\') }}?tab=comms" class="drawer-link"><i class="fas fa-bullhorn"></i> Communications</a>'
)

# Replace Student Drawer links
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-home"></i> Home Dashboard</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=home" class="drawer-link"><i class="fas fa-home"></i> Home Dashboard</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-calendar-alt"></i> Weekly Schedule</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=weekly" class="drawer-link"><i class="fas fa-calendar-alt"></i> Weekly Schedule</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-check-circle"></i> Meal Attendance</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=attendance" class="drawer-link"><i class="fas fa-check-circle"></i> Meal Attendance</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-comment-dots"></i> Student AI Assistant</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=agent" class="drawer-link"><i class="fas fa-comment-dots"></i> Student AI Assistant</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-envelope-open"></i> Leave Request</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=leave" class="drawer-link"><i class="fas fa-envelope-open"></i> Leave Request</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-exclamation-circle"></i> Submit Complaint</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=complaint" class="drawer-link"><i class="fas fa-exclamation-circle"></i> Submit Complaint</a>'
)
text = text.replace(
    '<a href="{{ url_for(\'student_portal\') }}" class="drawer-link"><i class="fas fa-cog"></i> Profile & Settings</a>',
    '<a href="{{ url_for(\'student_portal\') }}?tab=profile" class="drawer-link"><i class="fas fa-cog"></i> Profile & Settings</a>'
)

with open('templates/layout.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Layout deep links updated.")
