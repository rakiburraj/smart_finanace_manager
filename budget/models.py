from django.db import models
from department.models import Department

class MonthlyBudgetHistory(models.Model):
    department     = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='budget_history')
    year           = models.IntegerField()
    month          = models.IntegerField()
    allocated      = models.DecimalField(max_digits=12, decimal_places=2)
    total_expense  = models.DecimalField(max_digits=12, decimal_places=2)
    total_income   = models.DecimalField(max_digits=12, decimal_places=2)
    saved          = models.DecimalField(max_digits=12, decimal_places=2)
    carried_over   = models.DecimalField(max_digits=12, decimal_places=2)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['department', 'year', 'month']

    def __str__(self):
        return f"{self.department.name} — {self.month}/{self.year}"