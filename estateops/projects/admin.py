from django.contrib import admin

from .models import ProgressUpdate, Project, Flat


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "current_stage", "progress")


@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ("project", "stage", "progress", "created_at")


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ("project", "wing", "floor", "flat_number", "status")
    list_filter = ("project", "wing", "floor", "status")

