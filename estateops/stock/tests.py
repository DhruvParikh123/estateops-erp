from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from .models import StockItem, StockUsage

User = get_user_model()


class StockUsageTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Test Project",
            code="TST-01"
        )
        self.admin_user = User.objects.create_user(
            username="adminuser",
            password="password123",
            role="PROJECT_ADMIN",
            project=self.project
        )
        self.regular_user = User.objects.create_user(
            username="regularuser",
            password="password123",
            role="EMPLOYEE",
            project=self.project
        )
        self.stock_item = StockItem.objects.create(
            item="Cement Bags",
            price=400.00,
            available=100,
            threshold=10,
            project=self.project
        )

    def test_record_stock_usage_success(self):
        self.client.login(username="adminuser", password="password123")
        url = reverse("stock:usage_create", kwargs={"project_id": self.project.id})
        
        response = self.client.post(url, {
            "stock_item": self.stock_item.id,
            "quantity_used": 20,
            "date": "2026-07-04",
            "note": "Block A foundations"
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify quantity deducted
        self.stock_item.refresh_from_db()
        self.assertEqual(self.stock_item.available, 80)
        
        # Verify usage log created
        usages = StockUsage.objects.filter(project=self.project)
        self.assertEqual(usages.count(), 1)
        self.assertEqual(usages.first().quantity_used, 20)

    def test_record_stock_usage_insufficient_stock(self):
        self.client.login(username="adminuser", password="password123")
        url = reverse("stock:usage_create", kwargs={"project_id": self.project.id})
        
        # Try to use 120 bags when only 100 exist
        response = self.client.post(url, {
            "stock_item": self.stock_item.id,
            "quantity_used": 120,
            "date": "2026-07-04",
            "note": "Block B brickwork"
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify quantity NOT deducted
        self.stock_item.refresh_from_db()
        self.assertEqual(self.stock_item.available, 100)
        
        # Verify NO usage log created
        usages = StockUsage.objects.filter(project=self.project)
        self.assertEqual(usages.count(), 0)

    def test_unauthorized_user_cannot_record_usage(self):
        self.client.login(username="regularuser", password="password123")
        url = reverse("stock:usage_create", kwargs={"project_id": self.project.id})
        
        response = self.client.post(url, {
            "stock_item": self.stock_item.id,
            "quantity_used": 10,
            "date": "2026-07-04"
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify stock unaffected
        self.stock_item.refresh_from_db()
        self.assertEqual(self.stock_item.available, 100)
