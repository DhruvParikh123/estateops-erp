from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()


class ReportsAccessTests(TestCase):
    def setUp(self):
        # Create a test project
        self.project = Project.objects.create(
            name="Test Workspace",
            code="TST-01"
        )
        
        # Create a super admin
        self.super_admin = User.objects.create_superuser(
            username="super_admin",
            password="password123",
            role="SUPER_ADMIN"
        )
        
        # Create a project admin for this project
        self.proj_admin = User.objects.create_user(
            username="proj_admin",
            password="password123",
            role="PROJECT_ADMIN",
            project=self.project
        )
        
        # Create an employee assigned to this project (should be denied reports)
        self.employee = User.objects.create_user(
            username="employee_test",
            password="password123",
            role="EMPLOYEE",
            project=self.project
        )

    def test_unauthenticated_user_redirected(self):
        """Unauthenticated users should be redirected to login."""
        response = self.client.get(reverse("projects:reports", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_unauthorized_role_denied_access(self):
        """Employees should not be allowed to access workspace reports (403 Permission Denied)."""
        self.client.login(username="employee_test", password="password123")
        response = self.client.get(reverse("projects:reports", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 403)

        # Verify CSV access is also denied
        response_leads = self.client.get(reverse("projects:reports_export_leads", kwargs={"project_id": self.project.id}))
        self.assertEqual(response_leads.status_code, 403)

    def test_authorized_users_allowed_access(self):
        """Super admin and project admin should successfully access reports and export CSVs."""
        # 1. Test Project Admin
        self.client.login(username="proj_admin", password="password123")
        response = self.client.get(reverse("projects:reports", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/workspace_reports.html")

        # Test CSV export for Project Admin
        response_leads = self.client.get(reverse("projects:reports_export_leads", kwargs={"project_id": self.project.id}))
        self.assertEqual(response_leads.status_code, 200)
        self.assertEqual(response_leads["Content-Type"], "text/csv")
        self.assertIn("attachment; filename=", response_leads["Content-Disposition"])

        # 2. Test Super Admin
        self.client.login(username="super_admin", password="password123")
        response_super = self.client.get(reverse("projects:reports", kwargs={"project_id": self.project.id}))
        self.assertEqual(response_super.status_code, 200)
