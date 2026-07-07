from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("projects/<int:project_id>/leads/", views.lead_list, name="list"),
    path("projects/<int:project_id>/leads/create/", views.lead_create, name="create"),
    path("projects/<int:project_id>/leads/<int:pk>/followup/", views.followup_create, name="followup"),
]
