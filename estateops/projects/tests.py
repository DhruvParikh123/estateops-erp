from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project, Flat

User = get_user_model()


class FlatManagementTests(TestCase):
    def setUp(self):
        # Create a test project
        self.project = Project.objects.create(
            name="Ahmed Ahmedabad",
            code="AMD-01"
        )
        
        # Create test users
        self.super_admin = User.objects.create_superuser(
            username="super_admin",
            password="password123",
            role="SUPER_ADMIN"
        )
        
        self.proj_admin = User.objects.create_user(
            username="proj_admin",
            password="password123",
            role="PROJECT_ADMIN",
            project=self.project
        )
        
        self.employee = User.objects.create_user(
            username="employee_user",
            password="password123",
            role="EMPLOYEE",
            project=self.project
        )
        
        self.hr = User.objects.create_user(
            username="hr_user",
            password="password123",
            role="HR",
            project=self.project
        )
        
        # Create a sample flat
        self.flat = Flat.objects.create(
            project=self.project,
            wing="A",
            floor="1st",
            flat_number="101",
            status="AVAILABLE",
            created_by=self.super_admin
        )

    def test_unauthenticated_user_redirected(self):
        """Unauthenticated users should be redirected to login page."""
        response = self.client.get(reverse("projects:flat_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_unauthorized_roles_denied(self):
        """HR role should not be allowed to access flat management (403)."""
        self.client.login(username="hr_user", password="password123")
        response = self.client.get(reverse("projects:flat_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 403)

    def test_authorized_roles_allowed(self):
        """Super Admin, Project Admin, and Employee should be allowed access."""
        # 1. Super Admin
        self.client.login(username="super_admin", password="password123")
        response = self.client.get(reverse("projects:flat_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/flat_list.html")

        # 2. Project Admin
        self.client.login(username="proj_admin", password="password123")
        response = self.client.get(reverse("projects:flat_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)

        # 3. Employee
        self.client.login(username="employee_user", password="password123")
        response = self.client.get(reverse("projects:flat_list", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)

    def test_flat_creation(self):
        """Authorized user should be able to create a new flat."""
        self.client.login(username="employee_user", password="password123")
        url = reverse("projects:flat_create", kwargs={"project_id": self.project.id})
        data = {
            "wing": "B",
            "floor": "2nd",
            "flat_number": "202",
            "flat_type": "2BHK",
            "status": "UNDER_CONSTRUCTION"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect to list
        self.assertTrue(Flat.objects.filter(wing="B", floor="2nd", flat_number="202").exists())

    def test_flat_edit(self):
        """Authorized user should be able to edit flat details."""
        self.client.login(username="proj_admin", password="password123")
        url = reverse("projects:flat_edit", kwargs={"project_id": self.project.id, "flat_id": self.flat.id})
        data = {
            "wing": "A",
            "floor": "1st",
            "flat_number": "101",
            "flat_type": "2BHK",
            "status": "SOLD",
            "client_name": "Jane Doe",
            "client_phone": "9876543210",
            "booking_date": "2026-07-06",
            "price": 4500000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.flat.refresh_from_db()
        self.assertEqual(self.flat.status, "SOLD")
        self.assertEqual(self.flat.client_name, "Jane Doe")
        self.assertEqual(self.flat.price, 4500000)

    def test_flat_delete(self):
        """Authorized user should be able to delete a flat."""
        self.client.login(username="super_admin", password="password123")
        url = reverse("projects:flat_delete", kwargs={"project_id": self.project.id, "flat_id": self.flat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Flat.objects.filter(id=self.flat.id).exists())

    def test_flat_uniqueness(self):
        """Duplicate flat configurations (wing, floor, flat_number) within the same project should not be allowed."""
        self.client.login(username="super_admin", password="password123")
        # Try to create a flat with duplicate details (A, 1st, 101)
        url = reverse("projects:flat_create", kwargs={"project_id": self.project.id})
        data = {
            "wing": "A",
            "floor": "1st",
            "flat_number": "101",
            "flat_type": "2BHK",
            "status": "AVAILABLE"
        }
        response = self.client.post(url, data)
        # Form should be invalid and redirect back to flat list, showing error in messages
        self.assertEqual(response.status_code, 302)
        # Should not create duplicate flat (database unique constraint)
        self.assertEqual(Flat.objects.filter(wing="A", floor="1st", flat_number="101").count(), 1)

    def test_flat_quick_booking(self):
        """Should be able to book an available flat and set occupant details."""
        self.client.login(username="proj_admin", password="password123")
        
        # Create an available flat
        flat = Flat.objects.create(
            project=self.project,
            wing="A",
            floor="3rd",
            flat_number="303",
            flat_type="3BHK",
            status="AVAILABLE"
        )
        
        url = reverse("projects:flat_book", kwargs={"project_id": self.project.id, "flat_id": flat.id})
        data = {
            "client_name": "Resident XYZ",
            "client_phone": "1234567890",
            "family_members": "Member 1, Member 2",
            "booking_date": "2026-07-06",
            "price": 6000000
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
        flat.refresh_from_db()
        self.assertEqual(flat.status, "BOOKED")
        self.assertEqual(flat.client_name, "Resident XYZ")
        self.assertEqual(flat.client_phone, "1234567890")
        self.assertEqual(flat.family_members, "Member 1, Member 2")
        self.assertEqual(str(flat.booking_date), "2026-07-06")
        self.assertEqual(flat.price, 6000000)

    def test_flat_release_booking(self):
        """Should be able to release a booking, clearing booking/occupant details."""
        self.client.login(username="super_admin", password="password123")
        
        # Create a booked flat
        flat = Flat.objects.create(
            project=self.project,
            wing="A",
            floor="4th",
            flat_number="404",
            flat_type="4BHK",
            status="BOOKED",
            client_name="Old Resident",
            client_phone="9999999999",
            family_members="Spouse",
            booking_date="2026-01-01",
            price=8000000
        )
        
        url = reverse("projects:flat_release", kwargs={"project_id": self.project.id, "flat_id": flat.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        
        flat.refresh_from_db()
        self.assertEqual(flat.status, "AVAILABLE")
        self.assertNil = lambda x: self.assertIsNone(x)
        self.assertIsNone(flat.client_name)
        self.assertIsNone(flat.client_phone)
        self.assertIsNone(flat.family_members)
        self.assertIsNone(flat.booking_date)
        self.assertIsNone(flat.price)


