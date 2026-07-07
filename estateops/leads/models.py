from django.conf import settings
from django.db import models


class Lead(models.Model):
    class Requirement(models.TextChoices):
        ONE_BHK = "1BHK", "1BHK"
        TWO_BHK = "2BHK", "2BHK"
        THREE_BHK = "3BHK", "3BHK"
        FOUR_BHK = "4BHK", "4BHK"
        VILLA = "VILLA", "Villa"
        PLOT = "PLOT", "Plot"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INTERESTED = "interested", "Interested"
        LOST = "lost", "Lost"
        CONVERTED = "converted", "Converted"

    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="leads", null=True, blank=True)
    client_name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)
    requirement = models.CharField(max_length=10, choices=Requirement.choices, default=Requirement.TWO_BHK)
    source = models.CharField(max_length=120, blank=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    planned_followups = models.PositiveIntegerField(default=3)
    next_followup_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def budget_display(self):
        if self.budget_min and self.budget_max:
            return f"{int(self.budget_min):,}\u2013{int(self.budget_max):,}"
        if self.budget_min:
            return f"from {int(self.budget_min):,}"
        return "\u2014"

    def is_not_interested(self):
        return self.followups.filter(outcome="not_interested").exists()

    def can_followup(self):
        if self.status in [self.Status.LOST, self.Status.CONVERTED]:
            return False
        if self.followups.count() >= 3:
            return False
        if self.is_not_interested():
            return False
        return True

    def __str__(self):
        return self.client_name


class FollowUp(models.Model):
    class Outcome(models.TextChoices):
        INTERESTED = "interested", "Interested \u2014 keep in queue"
        NOT_INTERESTED = "not_interested", "Not interested"
        LOST = "lost", "Lost"
        CONVERTED = "converted", "Converted \u2014 close deal"
        NO_RESPONSE = "no_response", "No response"

    lead = models.ForeignKey(Lead, related_name="followups", on_delete=models.CASCADE)
    outcome = models.CharField(max_length=20, choices=Outcome.choices, default=Outcome.INTERESTED)
    next_followup_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.lead.client_name} - {self.outcome}"
