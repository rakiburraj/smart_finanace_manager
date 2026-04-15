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

def individual_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user and user.role == 'individual':
            login(request, user)
            return redirect('individuals:dashboard')
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/individual_login.html')

def finance_head_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user and user.role == 'finance_head':
            login(request, user)
            return redirect('department:head_dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/finance_head_login.html')

def dept_rep_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user and user.role == 'dept_rep':
            login(request, user)
            return redirect('department:rep_dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/dept_rep_login.html')

def logout_view(request):
    logout(request)
    return redirect('/')
