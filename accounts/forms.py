from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class IndividualRegisterForm(UserCreationForm):
    first_name      = forms.CharField(max_length=100)
    last_name       = forms.CharField(max_length=100)
    email           = forms.EmailField()
    profession      = forms.CharField(max_length=100)
    monthly_income  = forms.DecimalField(max_digits=12, decimal_places=2)
    monthly_expense = forms.DecimalField(max_digits=12, decimal_places=2)
    income_source   = forms.CharField(max_length=200)
    profile_pic     = forms.ImageField(required=False)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'profession',
                  'monthly_income', 'monthly_expense', 'income_source',
                  'profile_pic', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username       = self.cleaned_data['email']
        user.email          = self.cleaned_data['email']
        user.first_name     = self.cleaned_data['first_name']
        user.last_name      = self.cleaned_data['last_name']
        user.profession     = self.cleaned_data['profession']
        user.monthly_income = self.cleaned_data['monthly_income']
        user.monthly_expense= self.cleaned_data['monthly_expense']
        user.income_source  = self.cleaned_data['income_source']
        user.role           = 'individual'
        if commit:
            user.save()
        return user


class CompanyRegisterForm(UserCreationForm):
    company_name        = forms.CharField(max_length=200)
    company_address     = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    company_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    company_email       = forms.EmailField()
    monthly_income      = forms.DecimalField(max_digits=12, decimal_places=2)
    monthly_expense     = forms.DecimalField(max_digits=12, decimal_places=2)
    first_name          = forms.CharField(max_length=100, label='Finance Head Name')

    class Meta:
        model  = User
        fields = ['company_name', 'company_address', 'company_description',
                  'company_email', 'monthly_income', 'monthly_expense',
                  'first_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username            = self.cleaned_data['company_email']
        user.email               = self.cleaned_data['company_email']
        user.first_name          = self.cleaned_data['first_name']
        user.company_name        = self.cleaned_data['company_name']
        user.company_address     = self.cleaned_data['company_address']
        user.company_description = self.cleaned_data['company_description']
        user.company_email       = self.cleaned_data['company_email']
        user.monthly_income      = self.cleaned_data['monthly_income']
        user.monthly_expense     = self.cleaned_data['monthly_expense']
        user.role                = 'finance_head'
        if commit:
            user.save()
        return user
from django import forms
from .models import User


class IndividualUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'profile_pic',
            'profession',
            'monthly_income',
            'monthly_expense',
            'income_source',
        ]    
    