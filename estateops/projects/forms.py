from django import forms
from accounts.models import User
from .models import Project, Employee, Visitor, Asset, Leave, ProgressUpdate, Flat


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name", "code", "location_type", 
            "address", "city", "state", "pincode", "status"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Project Name"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Project Code (e.g. AMD-01)"}),
            "location_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "Location Type (e.g. Ahmedabad)"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Site Address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": "form-control", "placeholder": "State"}),
            "pincode": forms.TextInput(attrs={"class": "form-control", "placeholder": "Pincode"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "name", "email", "mobile", "department", "designation", 
            "joining_date", "photo", "aadhaar", "address", "status"
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email Address"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile Number"}),
            "department": forms.TextInput(attrs={"class": "form-control", "placeholder": "Department (e.g. Construction)"}),
            "designation": forms.TextInput(attrs={"class": "form-control", "placeholder": "Designation (e.g. Supervisor)"}),
            "joining_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "aadhaar": forms.TextInput(attrs={"class": "form-control", "placeholder": "Aadhaar Card Number"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Permanent Address"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ["name", "mobile", "purpose", "contact_person"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Visitor Full Name"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile Number"}),
            "purpose": forms.TextInput(attrs={"class": "form-control", "placeholder": "Purpose of Visit"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control", "placeholder": "Whom to Meet"}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ["name", "code", "value", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asset Name"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asset Code/Serial"}),
            "value": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Value in INR"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Description"}),
        }


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ["employee", "start_date", "end_date", "reason"]
        widgets = {
            "employee": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Reason for Leave"}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        if project:
            # Filter employee choices to this project
            self.fields["employee"].queryset = Employee.objects.filter(project=project, status="ACTIVE")


class ProjectUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))

    class Meta:
        model = User
        fields = ["username", "email", "password", "role"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email (Optional)"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude SUPER_ADMIN from role choices for project-level user creation
        role_choices = [
            (role, label) for role, label in User.Role.choices if role != User.Role.SUPER_ADMIN
        ]
        self.fields["role"].choices = role_choices


class ProgressUpdateForm(forms.ModelForm):
    class Meta:
        model = ProgressUpdate
        fields = ["stage", "progress", "message", "photo"]
        widgets = {
            "stage": forms.Select(attrs={"class": "form-select"}),
            "progress": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Message"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class FlatForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = ["wing", "floor", "flat_number", "flat_type", "status", "client_name", "client_phone", "family_members", "booking_date", "price"]
        widgets = {
            "wing": forms.TextInput(attrs={"class": "form-control", "placeholder": "Wing (e.g. A, B)"}),
            "floor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Floor (e.g. 1st, 2nd)"}),
            "flat_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Flat Number (e.g. 101, 201)"}),
            "flat_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select", "onchange": "toggleBookingFields(this)"}),
            "client_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Resident/Client Name"}),
            "client_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile Number"}),
            "family_members": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Family Members (if applicable)"}),
            "booking_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Booking/Selling Price"}),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        wing = cleaned_data.get("wing")
        floor = cleaned_data.get("floor")
        flat_number = cleaned_data.get("flat_number")
        status = cleaned_data.get("status")
        client_name = cleaned_data.get("client_name")
        booking_date = cleaned_data.get("booking_date")
        price = cleaned_data.get("price")

        # Validate that client details are present when booked or sold
        if status in [Flat.Status.BOOKED, Flat.Status.SOLD]:
            if not client_name:
                self.add_error("client_name", "Resident name is required when flat is booked or sold.")
            if not booking_date:
                self.add_error("booking_date", "Booking date is required when flat is booked or sold.")
            if not price:
                self.add_error("price", "Price is required when flat is booked or sold.")

        if self.project and wing and floor and flat_number:
            # Check if this flat already exists (excluding the current instance if editing)
            query = Flat.objects.filter(
                project=self.project,
                wing=wing,
                floor=floor,
                flat_number=flat_number
            )
            if self.instance and self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            if query.exists():
                raise forms.ValidationError("A flat with this wing, floor, and flat number already exists in this project.")
        return cleaned_data


class FlatBookingForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = ["client_name", "client_phone", "family_members", "booking_date", "price"]
        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Resident Name"}),
            "client_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile Number"}),
            "family_members": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Family Members (if applicable)"}),
            "booking_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Booking Price"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        client_name = cleaned_data.get("client_name")
        client_phone = cleaned_data.get("client_phone")
        booking_date = cleaned_data.get("booking_date")
        price = cleaned_data.get("price")

        if not client_name:
            self.add_error("client_name", "Resident Name is required for booking.")
        if not client_phone:
            self.add_error("client_phone", "Mobile Number is required for booking.")
        if not booking_date:
            self.add_error("booking_date", "Booking Date is required.")
        if not price:
            self.add_error("price", "Booking Price is required.")
        return cleaned_data
