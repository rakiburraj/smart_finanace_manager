from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('individual', 'Individual'),
        ('dept_rep', 'Department Rep'),
        ('finance_head', 'Finance Head'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='individual')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    
    profession = models.CharField(max_length=100, blank=True, null=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    monthly_expense = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    income_source = models.CharField(max_length=200, blank=True, null=True)

    
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_address = models.TextField(blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
