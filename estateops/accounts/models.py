from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with a role flag and project association used for multi-project tenant check."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        PROJECT_ADMIN = "PROJECT_ADMIN", "Project Admin"
        HR = "HR", "HR"
        SECURITY = "SECURITY", "Security"
        EMPLOYEE = "EMPLOYEE", "Employee"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_users"
    )

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_admin_role(self):
        return self.role in [self.Role.SUPER_ADMIN, self.Role.PROJECT_ADMIN] or self.is_superuser

    def __str__(self):
        project_name = self.project.name if self.project else "Global"
        return f"{self.username} ({self.get_role_display()} - {project_name})"
