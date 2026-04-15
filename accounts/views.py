from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import IndividualRegisterForm, CompanyRegisterForm

def individual_register(request):
    form = IndividualRegisterForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        user = form.save()
        messages.success(request, 'Account created! Please log in.')
        return redirect('accounts:individual_login')
    return render(request, 'accounts/individual_register.html', {'form': form})

def company_register(request):
    form = CompanyRegisterForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        user = form.save()
        messages.success(request, 'Company registered! Please log in.')
        return redirect('accounts:finance_head_login')
    return render(request, 'accounts/company_register.html', {'form': form})