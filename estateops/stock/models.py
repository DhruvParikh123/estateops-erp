from django.db import models
from django.utils import timezone


class StockItem(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="stock_items", null=True, blank=True)
    item = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    available = models.PositiveIntegerField(default=0)
    threshold = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["item"]

    @property
    def is_low(self):
        return self.available <= self.threshold

    def __str__(self):
        return self.item


class StockUsage(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="stock_usages")
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="usages")
    quantity_used = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, related_name="stock_usages_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.quantity_used} of {self.stock_item.item} on {self.date}"
