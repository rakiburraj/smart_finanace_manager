from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    monthly_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    carried_over = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    finance_head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='departments'
    )

    
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    def total_budget(self):
        return self.monthly_budget + self.carried_over

    def __str__(self):
        return self.name


class DepartmentRep(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    department = models.OneToOneField(
        Department,
        on_delete=models.CASCADE,
        related_name='rep'
    )

    plain_password = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} → {self.department.name}"



class DepartmentTransaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense')
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='transactions'
    )

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='expense'
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    date = models.DateField()

    receipt = models.FileField(
        upload_to='receipts/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']



class BudgetRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='budget_requests'
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='budget_requests_made'
    )

    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    
    request_date = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    response_date = models.DateTimeField(
        null=True,
        blank=True
    )

    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='budget_responses'
    )

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.department.name} - {self.requested_amount} ({self.status})"