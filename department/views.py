from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import date, timedelta
import json
from .models import Department, DepartmentRep, DepartmentTransaction, BudgetRequest
from .forms import (DepartmentForm, AssignRepForm, DeptTransactionForm,
                    BudgetRequestForm, BudgetUpdateForm)

User = get_user_model()


@login_required
def head_dashboard(request):
    if request.user.role != 'finance_head':
        return redirect('/')

    departments = Department.objects.filter(finance_head=request.user)
    today = date.today()

   
    total_budget  = sum(d.total_budget() for d in departments)
    total_expense = 0
    total_income  = 0
    for d in departments:
        txns = d.transactions.filter(date__year=today.year, date__month=today.month)
        total_expense += float(txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
        total_income  += float(txns.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0)

    pending_requests = BudgetRequest.objects.filter(
        department__in=departments, status='pending'
    ).count()

    
    m_labels, m_income, m_expense = [], [], []
    for i in range(5, -1, -1):
        mo = today.month - i
        yr = today.year
        if mo <= 0:
            mo += 12
            yr -= 1
        m_labels.append(date(yr, mo, 1).strftime('%b %Y'))
        inc = DepartmentTransaction.objects.filter(
            department__in=departments, date__year=yr, date__month=mo, type='income'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = DepartmentTransaction.objects.filter(
            department__in=departments, date__year=yr, date__month=mo, type='expense'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        m_income.append(float(inc))
        m_expense.append(float(exp))

    
    dept_summary = []
    for d in departments:
        txns = d.transactions.filter(date__year=today.year, date__month=today.month)
        spent = float(txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
        earned = float(txns.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
        budget = float(d.total_budget())
        pct = round((spent / budget * 100)) if budget > 0 else 0
        dept_summary.append({
            'dept': d, 'spent': spent, 'earned': earned,
            'budget': budget, 'pct': min(pct, 100),
            'remaining': max(budget - spent, 0),
            'has_rep': hasattr(d, 'rep'),
        })

    return render(request, 'department/head_dashboard.html', {
        'departments': departments,
        'dept_summary': dept_summary,
        'total_budget': total_budget,
        'total_expense': total_expense,
        'total_income': total_income,
        'pending_requests': pending_requests,
        'm_labels':  json.dumps(m_labels),
        'm_income':  json.dumps(m_income),
        'm_expense': json.dumps(m_expense),
        'today': today,
    })


@login_required
def create_department(request):
    if request.user.role != 'finance_head':
        return redirect('/')
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        dept = form.save(commit=False)
        dept.finance_head = request.user
        dept.save()
        messages.success(request, f'Department "{dept.name}" created!')
        return redirect('department:assign_rep', dept_id=dept.id)
    return render(request, 'department/create_department.html', {'form': form})


@login_required
def assign_rep(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id, finance_head=request.user)
    form = AssignRepForm(request.POST or None)
    if form.is_valid():
        email    = form.cleaned_data['rep_email']
        name     = form.cleaned_data['rep_name']
        password = form.cleaned_data['password']

        
        if hasattr(dept, 'rep'):
            old_user = dept.rep.user
            dept.rep.delete()
            old_user.delete()

        
        user = User.objects.create_user(
            username=email, email=email,
            first_name=name, password=password,
            role='dept_rep'
        )
        DepartmentRep.objects.create(user=user, department=dept, plain_password=password)
        messages.success(request, f'Rep "{name}" assigned to {dept.name}!')
        return redirect('department:head_dashboard')
    return render(request, 'department/assign_rep.html', {'form': form, 'dept': dept})


@login_required
def remove_rep(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id, finance_head=request.user)
    if hasattr(dept, 'rep'):
        rep_name = dept.rep.user.first_name
        old_user = dept.rep.user
        dept.rep.delete()
        old_user.delete()
        messages.success(request, f'Rep "{rep_name}" removed.')
    return redirect('department:head_dashboard')
