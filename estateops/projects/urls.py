from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # Project Administration (Global level - Super Admin)
    path("create/", views.project_create, name="create"),
    path("<int:project_id>/edit/", views.project_edit, name="edit"),
    path("<int:project_id>/delete/", views.project_delete, name="delete"),

    # Project Workspace (Project level - Scoped to project_id)
    path("<int:project_id>/dashboard/", views.project_dashboard, name="dashboard"),
    path("<int:project_id>/update/", views.progress_update, name="update"),
    
    # Employees
    path("<int:project_id>/employees/", views.employee_list, name="employee_list"),
    path("<int:project_id>/employees/add/", views.employee_create, name="employee_create"),
    path("<int:project_id>/employees/<int:emp_id>/edit/", views.employee_edit, name="employee_edit"),
    path("<int:project_id>/employees/<int:emp_id>/delete/", views.employee_delete, name="employee_delete"),
    
    # Attendance
    path("<int:project_id>/attendance/", views.attendance_list, name="attendance_list"),
    path("<int:project_id>/attendance/log/", views.attendance_log, name="attendance_log"),
    
    # Visitors
    path("<int:project_id>/visitors/", views.visitor_list, name="visitor_list"),
    path("<int:project_id>/visitors/add/", views.visitor_create, name="visitor_create"),
    path("<int:project_id>/visitors/<int:visitor_id>/checkout/", views.visitor_checkout, name="visitor_checkout"),
    
    # Assets
    path("<int:project_id>/assets/", views.asset_list, name="asset_list"),
    path("<int:project_id>/assets/add/", views.asset_create, name="asset_create"),
    path("<int:project_id>/assets/<int:asset_id>/delete/", views.asset_delete, name="asset_delete"),
    
    # Leaves
    path("<int:project_id>/leaves/", views.leave_list, name="leave_list"),
    path("<int:project_id>/leaves/apply/", views.leave_apply, name="leave_apply"),
    path("<int:project_id>/leaves/<int:leave_id>/action/<str:action>/", views.leave_action, name="leave_action"),
    
    # Users
    path("<int:project_id>/users/", views.user_list, name="user_list"),
    path("<int:project_id>/users/add/", views.user_create, name="user_create"),
    path("<int:project_id>/users/<int:user_id>/reset-password/", views.user_reset_password, name="user_reset_password"),
    
    # Project Reports
    path("<int:project_id>/reports/", views.workspace_reports, name="reports"),
    path("<int:project_id>/reports/export/leads/", views.workspace_reports_export_leads, name="reports_export_leads"),
    path("<int:project_id>/reports/export/followups/", views.workspace_reports_export_followups, name="reports_export_followups"),

    # Flats Management
    path("<int:project_id>/flats/", views.flat_list, name="flat_list"),
    path("<int:project_id>/flats/add/", views.flat_create, name="flat_create"),
    path("<int:project_id>/flats/<int:flat_id>/edit/", views.flat_edit, name="flat_edit"),
    path("<int:project_id>/flats/<int:flat_id>/delete/", views.flat_delete, name="flat_delete"),
    path("<int:project_id>/flats/<int:flat_id>/book/", views.flat_book, name="flat_book"),
    path("<int:project_id>/flats/<int:flat_id>/release/", views.flat_release, name="flat_release"),
]
