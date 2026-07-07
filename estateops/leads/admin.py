from django.contrib import admin

from .models import FollowUp, Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("client_name", "mobile", "requirement", "status", "next_followup_date")
    list_filter = ("status", "requirement")
    search_fields = ("client_name", "mobile")


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ("lead", "outcome", "next_followup_date", "created_at")
