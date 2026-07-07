from django.conf import settings
from django.db import models
from django.utils import timezone


class Project(models.Model):
    class Stage(models.TextChoices):
        PLINTH = "Plinth", "Plinth"
        SLAB = "Slab", "Slab"
        BRICKWORK = "Brickwork", "Brickwork"
        PLASTER = "Plaster", "Plaster"
        FLOORING = "Flooring", "Flooring"
        FINISHING = "Finishing", "Finishing"
        HANDOVER = "Handover", "Handover"

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    client_name = models.CharField(max_length=150, blank=True, null=True)
    location_type = models.CharField(max_length=100, default="Ahmedabad", blank=True, null=True)
    # Keeping old location field for compatibility
    location = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive")],
        default="ACTIVE"
    )
    current_stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.PLINTH)
    progress = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            max_id = Project.objects.all().count() + 1
            self.code = f"PROJ-{max_id:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class ProgressUpdate(models.Model):
    project = models.ForeignKey(Project, related_name="updates", on_delete=models.CASCADE)
    stage = models.CharField(max_length=20, choices=Project.Stage.choices)
    progress = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    photo = models.ImageField(upload_to="progress_photos/", null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="progress_updates_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.name} - {self.stage} ({self.progress}%)"


class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    joining_date = models.DateField(default=timezone.now)
    photo = models.ImageField(upload_to="employee_photos/", null=True, blank=True)
    aadhaar = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[("ACTIVE", "Active"), ("INACTIVE", "Inactive")],
        default="ACTIVE"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="employees")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="employees_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.employee_id:
            max_id = Employee.objects.all().count() + 1
            self.employee_id = f"EMP-{max_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Present"
        ABSENT = "ABSENT", "Absent"
        LATE = "LATE", "Late"
        LEAVE = "LEAVE", "Leave"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attendances")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendances_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "employee__name"]
        unique_together = ("employee", "date")

    def __str__(self):
        return f"{self.employee.name} - {self.date}: {self.get_status_display()}"


class Visitor(models.Model):
    name = models.CharField(max_length=150)
    mobile = models.CharField(max_length=20)
    purpose = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=150)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="visitors")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitors_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-entry_time"]

    def __str__(self):
        return f"{self.name} - {self.entry_time}"


class Asset(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="assets")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("project", "code")

    def __str__(self):
        return f"{self.name} ({self.code})"


class Leave(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="leaves")
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="leaves")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="leaves_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.name} : {self.start_date} to {self.end_date} ({self.get_status_display()})"


class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salaries")
    month = models.CharField(max_length=7) # format YYYY-MM
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="salaries")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="salaries_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-month", "employee__name"]
        unique_together = ("employee", "month")

    def __str__(self):
        return f"{self.employee.name} - {self.month}: {self.net_salary}"


class IDCard(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="id_card")
    card_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="id_cards")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="idcards_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ID Card: {self.card_number} ({self.employee.name})"


class Flat(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        BOOKED = "BOOKED", "Booked"
        SOLD = "SOLD", "Sold"
        UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION", "Under Construction"

    class FlatType(models.TextChoices):
        ONE_BHK = "1BHK", "1BHK"
        TWO_BHK = "2BHK", "2BHK"
        THREE_BHK = "3BHK", "3BHK"
        FOUR_BHK = "4BHK", "4BHK"
        PENTHOUSE = "PENTHOUSE", "Penthouse"
        SHOP = "SHOP", "Shop"
        OFFICE = "OFFICE", "Office"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="flats")
    wing = models.CharField(max_length=50)
    floor = models.CharField(max_length=50)
    flat_number = models.CharField(max_length=50)
    flat_type = models.CharField(max_length=20, choices=FlatType.choices, default=FlatType.TWO_BHK)
    
    # Booking details (only filled if status is BOOKED or SOLD)
    client_name = models.CharField(max_length=150, blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)
    family_members = models.TextField(blank=True, null=True)
    booking_date = models.DateField(blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="flats_created")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["wing", "floor", "flat_number"]
        unique_together = ("project", "wing", "floor", "flat_number")

    def __str__(self):
        return f"Wing {self.wing} - Floor {self.floor} - Flat {self.flat_number} ({self.flat_type})"
