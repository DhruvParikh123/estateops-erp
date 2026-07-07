from django import forms

from .models import StockItem, StockUsage


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ["item", "price", "available", "threshold"]
        widgets = {
            "item": forms.TextInput(attrs={"class": "form-control", "placeholder": "Item name"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Price"}),
            "available": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Available qty"}),
            "threshold": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Threshold"}),
        }


class StockUsageForm(forms.ModelForm):
    class Meta:
        model = StockUsage
        fields = ["stock_item", "quantity_used", "date", "note"]
        widgets = {
            "stock_item": forms.Select(attrs={"class": "form-select"}),
            "quantity_used": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Quantity used"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "note": forms.Textarea(attrs={"class": "form-control", "placeholder": "Purpose/notes (e.g. Block A concrete layout)", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields["stock_item"].queryset = StockItem.objects.filter(project=project)
