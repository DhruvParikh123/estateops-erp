import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from projects.models import Project, Employee, Visitor, Attendance
from accounts.models import User


@login_required
def home(request):
    if request.user.is_super_admin:
        # Super Admin global dashboard view
        projects = Project.objects.all()
        total_projects = projects.count()
        total_employees = Employee.objects.count()
        total_users = User.objects.count()
        total_visitors = Visitor.objects.count()
        total_attendance_today = Attendance.objects.filter(date=datetime.date.today()).count()

        context = {
            "projects": projects,
            "total_projects": total_projects,
            "total_employees": total_employees,
            "total_users": total_users,
            "total_visitors": total_visitors,
            "total_attendance_today": total_attendance_today,
            "is_super_admin": True,
        }
        return render(request, "dashboard/global_dashboard.html", context)
    else:
        # Non-super-admin: redirect directly to assigned project workspace
        if request.user.project:
            return redirect("projects:dashboard", project_id=request.user.project.id)
        else:
            return render(request, "dashboard/no_project.html")

