from django.db import models
from django.conf import settings
from django.utils import timezone


class IndividualBudget(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    monthly_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Budget - {self.user.username}"


class IndividualTransaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ind_transactions'
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50)
    description = models.TextField()
    date = models.DateField()

    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type} - {self.amount}"
