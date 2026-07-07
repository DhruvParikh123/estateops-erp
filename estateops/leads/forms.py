from django import forms

from .models import FollowUp, Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "client_name", "mobile", "requirement", "source",
            "budget_min", "budget_max", "planned_followups",
            "next_followup_date", "notes",
        ]
        widgets = {
            "client_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Client name"}),
            "mobile": forms.TextInput(attrs={"class": "form-control", "placeholder": "Mobile number"}),
            "requirement": forms.Select(attrs={"class": "form-select"}),
            "source": forms.TextInput(attrs={"class": "form-control", "placeholder": "Source / Reference"}),
            "budget_min": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Budget min"}),
            "budget_max": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Budget max"}),
            "planned_followups": forms.NumberInput(attrs={"class": "form-control"}),
            "next_followup_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Notes"}),
        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ["outcome", "next_followup_date", "note"]
        widgets = {
            "outcome": forms.Select(attrs={"class": "form-select"}),
            "next_followup_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Note"}),
        }
