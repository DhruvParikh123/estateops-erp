from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from projects.models import Project
from .models import Lead, FollowUp

User = get_user_model()


class FollowUpAutoLossTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Test Project",
            code="TST-01"
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            role="USER",
            project=self.project
        )
        self.client.login(username="testuser", password="testpassword")
        self.lead = Lead.objects.create(
            client_name="John Doe",
            mobile="1234567890",
            requirement=Lead.Requirement.TWO_BHK,
            status=Lead.Status.ACTIVE,
            created_by=self.user,
            project=self.project,
            planned_followups=3
        )

    def test_auto_loss_on_third_no_response(self):
        url = reverse("leads:followup", kwargs={"project_id": self.project.id, "pk": self.lead.id})

        # 1st follow-up: No Response
        response = self.client.post(url, {
            "outcome": "no_response",
            "next_followup_date": "",
            "note": "First try"
        })
        self.lead.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.lead.status, Lead.Status.ACTIVE)
        self.assertEqual(self.lead.followups.count(), 1)
        self.assertTrue(self.lead.can_followup())

        # 2nd follow-up: No Response
        response = self.client.post(url, {
            "outcome": "no_response",
            "next_followup_date": "",
            "note": "Second try"
        })
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.ACTIVE)
        self.assertEqual(self.lead.followups.count(), 2)
        self.assertTrue(self.lead.can_followup())

        # 3rd follow-up: No Response (Should transition to LOST and disable further follow-ups)
        response = self.client.post(url, {
            "outcome": "no_response",
            "next_followup_date": "",
            "note": "Third try"
        })
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.LOST)
        self.assertEqual(self.lead.followups.count(), 3)
        self.assertFalse(self.lead.can_followup())

    def test_not_interested_disables_followups(self):
        url = reverse("leads:followup", kwargs={"project_id": self.project.id, "pk": self.lead.id})

        # 1st follow-up outcome: not_interested
        response = self.client.post(url, {
            "outcome": "not_interested",
            "next_followup_date": "",
            "note": "Not interested at this location."
        })
        self.lead.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.lead.is_not_interested())
        self.assertFalse(self.lead.can_followup())
