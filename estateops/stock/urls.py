from django.urls import path

from . import views

app_name = "stock"

urlpatterns = [
    path("projects/<int:project_id>/stock/", views.stock_list, name="list"),
    path("projects/<int:project_id>/stock/create/", views.stock_create, name="create"),
    path("projects/<int:project_id>/stock/<int:pk>/delete/", views.stock_delete, name="delete"),
    path("projects/<int:project_id>/stock/usage/", views.stock_usage_create, name="usage_create"),
]
