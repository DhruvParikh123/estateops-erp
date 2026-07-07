import csv
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from leads.models import Lead, FollowUp
from stock.models import StockItem
from .forms import (
    ProjectForm, EmployeeForm, VisitorForm, AssetForm, 
    LeaveForm, ProjectUserForm, ProgressUpdateForm, FlatForm, FlatBookingForm
)
from .models import Project, Employee, Attendance, Visitor, Asset, Leave, ProgressUpdate, Salary, IDCard, Flat


# Helper Functions
def get_project_or_deny(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.user.is_super_admin:
        return project
    if request.user.project and request.user.project.id == project.id:
        return project
    raise PermissionDenied("You do not have access to this project.")


def check_role_or_deny(user, allowed_roles):
    if user.is_super_admin:
        return
    if user.role in allowed_roles:
        return
    raise PermissionDenied("You do not have permission to perform this action.")


# Global Project Administration (Super Admin only)
@login_required
def project_create(request):
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN])
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            messages.success(request, f"Project '{project.name}' created successfully.")
        else:
            messages.error(request, "Failed to create project. Please verify inputs.")
    return redirect("dashboard:home")


@login_required
def project_edit(request, project_id):
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN])
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Project '{project.name}' updated successfully.")
        else:
            messages.error(request, "Failed to update project.")
    return redirect("dashboard:home")


@login_required
def project_delete(request, project_id):
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN])
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect("dashboard:home")


@login_required
def project_toggle_status(request, project_id):
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN])
    project = get_object_or_404(Project, id=project_id)
    project.status = "INACTIVE" if project.status == "ACTIVE" else "ACTIVE"
    project.save()
    messages.success(request, f"Project '{project.name}' status toggled to {project.status}.")
    return redirect("dashboard:home")


# Project Workspace View (Dashboard)
@login_required
def project_dashboard(request, project_id):
    project = get_project_or_deny(request, project_id)
    
    # Calculate stats for this project only
    employees = Employee.objects.filter(project=project)
    total_employees = employees.count()
    
    today = datetime.date.today()
    present_today = Attendance.objects.filter(
        project=project, date=today, status__in=["PRESENT", "LATE"]
    ).count()
    absent_today = Attendance.objects.filter(
        project=project, date=today, status="ABSENT"
    ).count()
    
    active_visitors = Visitor.objects.filter(project=project, exit_time__isnull=True).count()
    pending_leaves = Leave.objects.filter(project=project, status="PENDING").count()
    active_users = User.objects.filter(project=project, is_active=True).count()
    
    # Quick charts / breakdown data
    attendance_rate = int(present_today * 100 / total_employees) if total_employees else 0
    
    # Recent Activities log
    recent_activities = []
    # 1. Recent Employees added
    for emp in employees.order_by("-created_at")[:3]:
        recent_activities.append({
            "time": emp.created_at,
            "icon": "person_add",
            "class": "bg-primary text-white",
            "text": f"New Employee registered: {emp.name} ({emp.designation})"
        })
    # 2. Recent visitors logged
    for vis in Visitor.objects.filter(project=project).order_by("-entry_time")[:3]:
        action_text = f"Visitor checked in: {vis.name} to meet {vis.contact_person}"
        if vis.exit_time:
            action_text = f"Visitor checked out: {vis.name}"
        recent_activities.append({
            "time": vis.entry_time,
            "icon": "badge",
            "class": "bg-success text-white",
            "text": action_text
        })
    # 3. Recent leaves requested
    for l in Leave.objects.filter(project=project).order_by("-created_at")[:3]:
        recent_activities.append({
            "time": l.created_at,
            "icon": "date_range",
            "class": "bg-warning text-dark",
            "text": f"Leave Request: {l.employee.name} applied for {l.start_date} to {l.end_date}"
        })
        
    recent_activities = sorted(recent_activities, key=lambda x: x["time"], reverse=True)[:5]
    
    # Old project progress tracking
    progress_form = ProgressUpdateForm()
    progress_updates = ProgressUpdate.objects.filter(project=project)[:5]

    context = {
        "project": project,
        "total_employees": total_employees,
        "present_today": present_today,
        "absent_today": absent_today,
        "active_visitors": active_visitors,
        "pending_leaves": pending_leaves,
        "active_users": active_users,
        "attendance_rate": attendance_rate,
        "recent_activities": recent_activities,
        "progress_form": progress_form,
        "progress_updates": progress_updates,
    }
    return render(request, "projects/project_dashboard.html", context)


# Employees CRUD
@login_required
def employee_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    employees = Employee.objects.filter(project=project)
    form = EmployeeForm()
    
    context = {
        "project": project,
        "employees": employees,
        "form": form,
    }
    return render(request, "projects/employee_list.html", context)


@login_required
def employee_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            emp = form.save(commit=False)
            emp.project = project
            emp.created_by = request.user
            emp.save()
            messages.success(request, f"Employee '{emp.name}' registered successfully.")
        else:
            messages.error(request, "Failed to register employee. Check input details.")
    return redirect("projects:employee_list", project_id=project.id)


@login_required
def employee_edit(request, project_id, emp_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    emp = get_object_or_404(Employee, id=emp_id, project=project)
    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee '{emp.name}' updated successfully.")
            return redirect("projects:employee_list", project_id=project.id)
        messages.error(request, "Failed to update employee details.")
    else:
        form = EmployeeForm(instance=emp)
        
    context = {
        "project": project,
        "employee": emp,
        "form": form,
    }
    return render(request, "projects/employee_edit.html", context)


@login_required
def employee_delete(request, project_id, emp_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    emp = get_object_or_404(Employee, id=emp_id, project=project)
    emp.delete()
    messages.success(request, "Employee deleted successfully.")
    return redirect("projects:employee_list", project_id=project.id)


@login_required
def attendance_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR, User.Role.SECURITY, User.Role.EMPLOYEE])
    
    today = datetime.date.today()
    employees = Employee.objects.filter(project=project, status="ACTIVE")
    logged_today = Attendance.objects.filter(project=project, date=today)
    
    employees_data = []
    for emp in employees:
        att = logged_today.filter(employee=emp).first()
        status_val = att.status if att else "PRESENT"
        employees_data.append({
            "employee": emp,
            "status": status_val
        })
    
    history = Attendance.objects.filter(project=project).order_by("-date")[:100]
    
    context = {
        "project": project,
        "employees_data": employees_data,
        "history": history,
        "today": today,
    }
    return render(request, "projects/attendance_list.html", context)
    return render(request, "projects/attendance_list.html", context)


@login_required
def attendance_log(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR, User.Role.SECURITY ,User.Role.EMPLOYEE])
    
    if request.method == "POST":
        today = datetime.date.today()
        # Parse post parameters employee_id:status
        employees = Employee.objects.filter(project=project, status="ACTIVE")
        for emp in employees:
            status_val = request.POST.get(f"status_{emp.id}", "ABSENT")
            # Update or create attendance record
            Attendance.objects.update_or_create(
                employee=emp,
                date=today,
                defaults={
                    "status": status_val,
                    "project": project,
                    "created_by": request.user
                }
            )
        messages.success(request, "Daily Attendance logged successfully.")
    return redirect("projects:attendance_list", project_id=project.id)


# Visitors Logging
@login_required
def visitor_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [
        User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, 
        User.Role.HR, User.Role.SECURITY, User.Role.EMPLOYEE
    ])
    
    visitors = Visitor.objects.filter(project=project)
    form = VisitorForm()
    
    context = {
        "project": project,
        "visitors": visitors,
        "form": form,
    }
    return render(request, "projects/visitor_list.html", context)


@login_required
def visitor_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR, User.Role.SECURITY])
    
    if request.method == "POST":
        form = VisitorForm(request.POST)
        if form.is_valid():
            vis = form.save(commit=False)
            vis.project = project
            vis.created_by = request.user
            vis.save()
            messages.success(request, f"Visitor '{vis.name}' logged successfully.")
        else:
            messages.error(request, "Failed to log visitor.")
    return redirect("projects:visitor_list", project_id=project.id)


@login_required
def visitor_checkout(request, project_id, visitor_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR, User.Role.SECURITY])
    
    vis = get_object_or_404(Visitor, id=visitor_id, project=project)
    vis.exit_time = timezone.now()
    vis.save()
    messages.success(request, f"Visitor '{vis.name}' checked out successfully.")
    return redirect("projects:visitor_list", project_id=project.id)


# Assets CRUD
@login_required
def asset_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    assets = Asset.objects.filter(project=project)
    form = AssetForm()
    
    context = {
        "project": project,
        "assets": assets,
        "form": form,
    }
    return render(request, "projects/asset_list.html", context)


@login_required
def asset_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    if request.method == "POST":
        form = AssetForm(request.POST)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.project = project
            asset.created_by = request.user
            asset.save()
            messages.success(request, f"Asset '{asset.name}' added successfully.")
        else:
            messages.error(request, "Failed to add asset. Check for duplicate codes.")
    return redirect("projects:asset_list", project_id=project.id)


@login_required
def asset_delete(request, project_id, asset_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    asset = get_object_or_404(Asset, id=asset_id, project=project)
    asset.delete()
    messages.success(request, "Asset removed successfully.")
    return redirect("projects:asset_list", project_id=project.id)


# Leaves Handling
@login_required
def leave_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    
    # Employees can only request and see their leaves (or HR/Admins see all)
    leaves = Leave.objects.filter(project=project)
    form = LeaveForm(project=project)
    
    can_approve = request.user.is_super_admin or request.user.role in [User.Role.PROJECT_ADMIN, User.Role.HR]
    
    context = {
        "project": project,
        "leaves": leaves,
        "form": form,
        "can_approve": can_approve,
    }
    return render(request, "projects/leave_list.html", context)


@login_required
def leave_apply(request, project_id):
    project = get_project_or_deny(request, project_id)
    
    if request.method == "POST":
        form = LeaveForm(request.POST, project=project)
        if form.is_valid():
            l = form.save(commit=False)
            l.project = project
            l.created_by = request.user
            l.save()
            messages.success(request, "Leave request submitted successfully.")
        else:
            messages.error(request, "Failed to submit leave request.")
    return redirect("projects:leave_list", project_id=project.id)


@login_required
def leave_action(request, project_id, leave_id, action):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    leave = get_object_or_404(Leave, id=leave_id, project=project)
    if action == "approve":
        leave.status = "APPROVED"
        messages.success(request, "Leave request approved.")
    elif action == "reject":
        leave.status = "REJECTED"
        messages.success(request, "Leave request rejected.")
    leave.save()
    return redirect("projects:leave_list", project_id=project.id)


# Workspace Users (Super Admin and Project Admin only)
@login_required
def user_list(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN])
    
    users = User.objects.filter(project=project)
    form = ProjectUserForm()
    
    context = {
        "project": project,
        "users": users,
        "form": form,
    }
    return render(request, "projects/user_list.html", context)


@login_required
def user_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN])
    
    if request.method == "POST":
        form = ProjectUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.project = project
            user.password = make_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, f"User account '{user.username}' created successfully.")
        else:
            messages.error(request, "Failed to create user. Verify inputs / duplicates.")
    return redirect("projects:user_list", project_id=project.id)


@login_required
def user_reset_password(request, project_id, user_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN])
    
    user = get_object_or_404(User, id=user_id, project=project)
    if request.method == "POST":
        new_pwd = request.POST.get("new_password")
        if new_pwd:
            user.password = make_password(new_pwd)
            user.save()
            messages.success(request, f"Password reset successfully for '{user.username}'.")
        else:
            messages.error(request, "Password cannot be empty.")
    return redirect("projects:user_list", project_id=project.id)


# Local Project Reports
def parse_date_range_helper(request):
    today = timezone.localtime(timezone.now()).date()
    report_type = request.GET.get("type", "daily")
    date_str = request.GET.get("date", "")
    week_str = request.GET.get("week", "")
    month_str = request.GET.get("month", "")
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")

    start_date = today
    end_date = today

    if report_type == "daily":
        if date_str:
            try:
                start_date = end_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
    elif report_type == "weekly":
        if week_str:
            try:
                year_part, week_part = week_str.split("-W")
                start_date = datetime.date.fromisocalendar(int(year_part), int(week_part), 1)
                end_date = start_date + datetime.timedelta(days=6)
            except (ValueError, IndexError):
                pass
        else:
            start_date = today - datetime.timedelta(days=today.weekday())
            end_date = start_date + datetime.timedelta(days=6)
    elif report_type == "monthly":
        if month_str:
            try:
                year_part, month_part = month_str.split("-")
                y, m = int(year_part), int(month_part)
                start_date = datetime.date(y, m, 1)
                if m == 12:
                    end_date = datetime.date(y, 12, 31)
                else:
                    end_date = datetime.date(y, m + 1, 1) - datetime.timedelta(days=1)
            except (ValueError, IndexError):
                pass
        else:
            start_date = datetime.date(today.year, today.month, 1)
            if today.month == 12:
                end_date = datetime.date(today.year, 12, 31)
            else:
                end_date = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)
    elif report_type == "custom":
        if start_date_str and end_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        else:
            start_date = today - datetime.timedelta(days=30)
            end_date = today
            
    return start_date, end_date


@login_required
def workspace_reports(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    today = timezone.localtime(timezone.now()).date()

    report_type = request.GET.get("type", "daily")
    date_str = request.GET.get("date", "")
    week_str = request.GET.get("week", "")
    month_str = request.GET.get("month", "")
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")

    start_date, end_date = parse_date_range_helper(request)

    # Defaults for form inputs
    if report_type == "weekly" and not week_str:
        year, week_num, _ = today.isocalendar()
        week_str = f"{year}-W{week_num:02d}"
    elif report_type == "monthly" and not month_str:
        month_str = today.strftime("%Y-%m")
    elif report_type == "custom" and (not start_date_str or not end_date_str):
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

    # Fetch data in period (filtered by project)
    leads = Lead.objects.filter(project=project, created_at__date__range=(start_date, end_date))
    followups = FollowUp.objects.filter(lead__project=project, created_at__date__range=(start_date, end_date))
    progress_updates = ProgressUpdate.objects.filter(project=project, created_at__date__range=(start_date, end_date))
    attendance_records = Attendance.objects.filter(project=project, date__range=(start_date, end_date))
    visitor_records = Visitor.objects.filter(project=project, entry_time__date__range=(start_date, end_date))

    # Aggregated Stats
    total_new_leads = leads.count()
    total_followups = followups.count()
    deals_converted = followups.filter(outcome=FollowUp.Outcome.CONVERTED).count()
    updates_count = progress_updates.count()
    total_attendance = attendance_records.count()
    total_visitors = visitor_records.count()

    # Distribution calculations for charts
    req_counts = leads.values("requirement").annotate(count=models.Count("id"))
    req_labels = [item["requirement"] for item in req_counts]
    req_data = [item["count"] for item in req_counts]

    outcome_counts = followups.values("outcome").annotate(count=models.Count("id"))
    outcome_labels = [dict(FollowUp.Outcome.choices).get(item["outcome"], item["outcome"]) for item in outcome_counts]
    outcome_data = [item["count"] for item in outcome_counts]

    source_counts = leads.values("source").annotate(count=models.Count("id")).order_by("-count")[:5]
    top_sources = []
    for item in source_counts:
        top_sources.append({
            "source": item["source"] or "Unknown/Direct",
            "count": item["count"],
            "percentage": int(item["count"] * 100 / total_new_leads) if total_new_leads else 0
        })

    # Activity Trend (only generate if timeframe is reasonably sized, e.g. <= 62 days)
    trend_labels = []
    trend_leads = []
    trend_followups = []
    delta = end_date - start_date
    if delta.days <= 62:
        current = start_date
        while current <= end_date:
            trend_labels.append(current.strftime("%b %d"))
            trend_leads.append(leads.filter(created_at__date=current).count())
            trend_followups.append(followups.filter(created_at__date=current).count())
            current += datetime.timedelta(days=1)

    low_stock = StockItem.objects.filter(project=project, available__lte=models.F("threshold"))

    context = {
        "project": project,
        "report_type": report_type,
        "date_str": date_str or today.strftime("%Y-%m-%d"),
        "week_str": week_str,
        "month_str": month_str,
        "start_date_str": start_date_str,
        "end_date_str": end_date_str,
        "start_date": start_date,
        "end_date": end_date,
        
        "total_new_leads": total_new_leads,
        "total_followups": total_followups,
        "deals_converted": deals_converted,
        "updates_count": updates_count,
        "total_attendance": total_attendance,
        "total_visitors": total_visitors,

        "req_labels": req_labels,
        "req_data": req_data,
        "outcome_labels": outcome_labels,
        "outcome_data": outcome_data,
        "top_sources": top_sources,

        "trend_labels": trend_labels,
        "trend_leads": trend_leads,
        "trend_followups": trend_followups,

        "leads_list": leads[:50],
        "followups_list": followups[:50],
        "updates_list": progress_updates[:50],
        "low_stock_items": low_stock,
    }
    return render(request, "projects/workspace_reports.html", context)


@login_required
def workspace_reports_export_leads(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])

    start_date, end_date = parse_date_range_helper(request)
    leads = Lead.objects.filter(project=project, created_at__date__range=(start_date, end_date)).order_by("created_at")

    response = HttpResponse(content_type="text/csv")
    filename = f"leads_report_proj_{project.code}_{start_date}_to_{end_date}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        "Client Name", "Mobile", "Requirement", "Source", 
        "Min Budget", "Max Budget", "Status", "Created By", "Created At"
    ])

    for lead in leads:
        writer.writerow([
            lead.client_name,
            lead.mobile,
            lead.requirement,
            lead.source,
            lead.budget_min or "",
            lead.budget_max or "",
            lead.get_status_display(),
            lead.created_by.username if lead.created_by else "",
            timezone.localtime(lead.created_at).strftime("%Y-%m-%d %H:%M:%S")
        ])

    return response


@login_required
def workspace_reports_export_followups(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])

    start_date, end_date = parse_date_range_helper(request)
    followups = FollowUp.objects.filter(lead__project=project, created_at__date__range=(start_date, end_date)).order_by("created_at")

    response = HttpResponse(content_type="text/csv")
    filename = f"followups_report_proj_{project.code}_{start_date}_to_{end_date}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        "Lead Client Name", "Lead Mobile", "Outcome", 
        "Next Follow-up Date", "Note", "Logged By", "Logged At"
    ])

    for f in followups:
        writer.writerow([
            f.lead.client_name,
            f.lead.mobile,
            f.get_outcome_display(),
            f.next_followup_date or "",
            f.note,
            f.created_by.username if f.created_by else "",
            timezone.localtime(f.created_at).strftime("%Y-%m-%d %H:%M:%S")
        ])

    return response


@login_required
def progress_update(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.HR])
    
    if request.method == "POST":
        form = ProgressUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.project = project
            update.created_by = request.user
            update.save()

            project.current_stage = update.stage
            project.progress = update.progress
            project.save()

            messages.success(request, f"Update posted successfully for {project.name}.")
        else:
            messages.error(request, "Please check the update inputs.")
            
    return redirect("projects:dashboard", project_id=project.id)


# Flats CRUD
@login_required
def flat_list(request, project_id):
    from django.core.paginator import Paginator
    from django.db.models import Q, Sum
    
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.EMPLOYEE])
    
    # Calculate statistics based on ALL flats of the project
    all_flats = Flat.objects.filter(project=project)
    total_flats = all_flats.count()
    available_flats = all_flats.filter(status=Flat.Status.AVAILABLE).count()
    booked_flats = all_flats.filter(status=Flat.Status.BOOKED).count()
    sold_flats = all_flats.filter(status=Flat.Status.SOLD).count()
    under_construction = all_flats.filter(status=Flat.Status.UNDER_CONSTRUCTION).count()
    
    # Calculate total revenue / value from booked and sold flats
    total_value = all_flats.filter(status__in=[Flat.Status.BOOKED, Flat.Status.SOLD]).aggregate(Sum('price'))['price__sum'] or 0
    
    # Group stats by wing/ring (based on ALL flats)
    wing_stats_dict = {}
    for flat in all_flats:
        wing = flat.wing.upper()
        if wing not in wing_stats_dict:
            wing_stats_dict[wing] = {
                "total": 0,
                "available": 0,
                "booked": 0,
                "sold": 0,
                "under_construction": 0,
                "value": 0
            }
        wing_stats_dict[wing]["total"] += 1
        if flat.status == Flat.Status.AVAILABLE:
            wing_stats_dict[wing]["available"] += 1
        elif flat.status == Flat.Status.BOOKED:
            wing_stats_dict[wing]["booked"] += 1
            wing_stats_dict[wing]["value"] += flat.price or 0
        elif flat.status == Flat.Status.SOLD:
            wing_stats_dict[wing]["sold"] += 1
            wing_stats_dict[wing]["value"] += flat.price or 0
        elif flat.status == Flat.Status.UNDER_CONSTRUCTION:
            wing_stats_dict[wing]["under_construction"] += 1
            
    # Sort wing stats by wing name
    wing_stats = sorted([{"wing": k, **v} for k, v in wing_stats_dict.items()], key=lambda x: x["wing"])
    
    # Active Tab ('available', 'booked', 'all')
    tab = request.GET.get("tab", "available")
    if tab not in ["available", "booked", "all"]:
        tab = "available"
        
    # Get corresponding flats queryset
    flats_queryset = all_flats
    if tab == "available":
        flats_queryset = all_flats.filter(status=Flat.Status.AVAILABLE)
    elif tab == "booked":
        flats_queryset = all_flats.filter(status__in=[Flat.Status.BOOKED, Flat.Status.SOLD])
        
    # Server-side Search
    q = request.GET.get("q", "").strip()
    if q:
        flats_queryset = flats_queryset.filter(
            Q(flat_number__icontains=q) |
            Q(wing__icontains=q) |
            Q(client_name__icontains=q)
        )
        
    # Server-side Pagination (10 items per page)
    paginator = Paginator(flats_queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    form = FlatForm(project=project)
    booking_form = FlatBookingForm()
    
    context = {
        "project": project,
        "page_obj": page_obj,
        "tab": tab,
        "q": q,
        "form": form,
        "booking_form": booking_form,
        "total_flats": total_flats,
        "available_flats": available_flats,
        "booked_flats": booked_flats,
        "sold_flats": sold_flats,
        "under_construction": under_construction,
        "total_value": total_value,
        "wing_stats": wing_stats,
    }
    return render(request, "projects/flat_list.html", context)


@login_required
def flat_create(request, project_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.EMPLOYEE])
    
    if request.method == "POST":
        form = FlatForm(request.POST, project=project)
        if form.is_valid():
            flat = form.save(commit=False)
            flat.project = project
            flat.created_by = request.user
            flat.save()
            messages.success(request, f"Flat '{flat.flat_number}' in Wing '{flat.wing}' added successfully.")
        else:
            errors_str = " ".join([f"{field}: {error[0]}" for field, error in form.errors.items()])
            messages.error(request, f"Failed to add flat. {errors_str}")
    return redirect("projects:flat_list", project_id=project.id)


@login_required
def flat_edit(request, project_id, flat_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.EMPLOYEE])
    
    flat = get_object_or_404(Flat, id=flat_id, project=project)
    if request.method == "POST":
        form = FlatForm(request.POST, instance=flat, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Flat '{flat.flat_number}' updated successfully.")
            return redirect("projects:flat_list", project_id=project.id)
        errors_str = " ".join([f"{field}: {error[0]}" for field, error in form.errors.items()])
        messages.error(request, f"Failed to update flat details. {errors_str}")
    else:
        form = FlatForm(instance=flat, project=project)
        
    context = {
        "project": project,
        "flat": flat,
        "form": form,
    }
    return render(request, "projects/flat_edit.html", context)


@login_required
def flat_delete(request, project_id, flat_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.EMPLOYEE])
    
    flat = get_object_or_404(Flat, id=flat_id, project=project)
    flat.delete()
    messages.success(request, "Flat removed successfully.")
    return redirect("projects:flat_list", project_id=project.id)


@login_required
def flat_book(request, project_id, flat_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.EMPLOYEE])
    
    flat = get_object_or_404(Flat, id=flat_id, project=project)
    if flat.status == Flat.Status.BOOKED:
        messages.error(request, "This flat is already booked.")
        return redirect("projects:flat_list", project_id=project.id)
        
    if request.method == "POST":
        form = FlatBookingForm(request.POST, instance=flat)
        if form.is_valid():
            booked_flat = form.save(commit=False)
            booked_flat.status = Flat.Status.BOOKED
            booked_flat.save()
            messages.success(request, f"Flat '{flat.flat_number}' booked successfully for {flat.client_name}.")
        else:
            errors_str = " ".join([f"{field}: {error[0]}" for field, error in form.errors.items()])
            messages.error(request, f"Failed to book flat. {errors_str}")
    return redirect("projects:flat_list", project_id=project.id)


@login_required
def flat_release(request, project_id, flat_id):
    project = get_project_or_deny(request, project_id)
    check_role_or_deny(request.user, [User.Role.SUPER_ADMIN, User.Role.PROJECT_ADMIN, User.Role.EMPLOYEE])
    
    flat = get_object_or_404(Flat, id=flat_id, project=project)
    flat.status = Flat.Status.AVAILABLE
    flat.client_name = None
    flat.client_phone = None
    flat.family_members = None
    flat.booking_date = None
    flat.price = None
    flat.save()
    
    messages.success(request, f"Booking for Flat '{flat.flat_number}' released successfully.")
    return redirect("projects:flat_list", project_id=project.id)
