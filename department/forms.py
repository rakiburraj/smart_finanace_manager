from django import forms
from .models import Department, DepartmentTransaction, BudgetRequest
from django.contrib.auth import get_user_model

User = get_user_model()

class DepartmentForm(forms.ModelForm):
    class Meta:
        model  = Department
        fields = ['name', 'description', 'monthly_budget']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class AssignRepForm(forms.Form):
    rep_name  = forms.CharField(max_length=100, label='Rep Full Name')
    rep_email = forms.EmailField(label='Rep Email')
    password  = forms.CharField(
        max_length=50,
        label='Assign Password',
        widget=forms.TextInput(attrs={'placeholder': 'Create a password for them'})
    )

class DeptTransactionForm(forms.ModelForm):
    class Meta:
        model  = DepartmentTransaction
        fields = ['type', 'amount', 'description', 'date', 'receipt']
        widgets = {
            'date':        forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class BudgetRequestForm(forms.ModelForm):
    class Meta:
        model  = BudgetRequest
        fields = ['requested_amount', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class BudgetUpdateForm(forms.ModelForm):
    class Meta:
        model  = Department
        fields = ['monthly_budget']