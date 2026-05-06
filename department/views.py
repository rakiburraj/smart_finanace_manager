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


@login_required
def update_budget(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id, finance_head=request.user)
    form = BudgetUpdateForm(request.POST or None, instance=dept)
    if form.is_valid():
        form.save()
        messages.success(request, 'Budget updated!')
        return redirect('department:head_dashboard')
    return render(request, 'department/update_budget.html', {'form': form, 'dept': dept})


@login_required
def dept_detail(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id, finance_head=request.user)

    txns = dept.transactions.all()
    requests = dept.budget_requests.all()
    today = date.today()

    
    month_txns = txns.filter(date__year=today.year, date__month=today.month)

    month_expense = float(
        month_txns.filter(type='expense')
        .aggregate(Sum('amount'))['amount__sum'] or 0
    )

    month_income = float(
        month_txns.filter(type='income')
        .aggregate(Sum('amount'))['amount__sum'] or 0
    )

    total_budget = float(dept.total_budget())
    remaining = max(total_budget - month_expense, 0)

    pct_used = round((month_expense / total_budget * 100)) if total_budget > 0 else 0
    pct_used = min(pct_used, 100)
    budget_exceeded = month_expense >= total_budget and total_budget > 0

    
    labels, inc_data, exp_data = [], [], []

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%b %d'))

        inc_data.append(float(
            txns.filter(date=d, type='income')
            .aggregate(Sum('amount'))['amount__sum'] or 0
        ))

        exp_data.append(float(
            txns.filter(date=d, type='expense')
            .aggregate(Sum('amount'))['amount__sum'] or 0
        ))

    
    recent_txns = txns.order_by('-date')[:8]

    return render(request, 'department/dept_detail.html', {
        'dept': dept,
        'txns': txns,
        'requests': requests,

        
        'month_expense': month_expense,
        'month_income': month_income,
        'total_budget': total_budget,
        'remaining': remaining,
        'pct_used': pct_used,
        'budget_exceeded': budget_exceeded,

        # rep-style analytics
        'recent_txns': recent_txns,
        'labels': json.dumps(labels),
        'inc_data': json.dumps(inc_data),
        'exp_data': json.dumps(exp_data),
        'today': today,
    })


@login_required
def respond_budget(request, req_id, action):
    br   = get_object_or_404(BudgetRequest, id=req_id)
    dept = br.department
    if dept.finance_head != request.user:
        return redirect('/')
    if action == 'approve':
        dept.monthly_budget += br.requested_amount
        dept.save()
        br.status = 'approved'
        messages.success(request, f'Budget request approved! ৳{br.requested_amount} added.')
    elif action == 'reject':
        br.status = 'rejected'
        messages.warning(request, 'Budget request rejected.')
    br.responded_by   = request.user
    br.response_date  = timezone.now()
    br.save()
    return redirect('department:head_dashboard')




@login_required
def rep_dashboard(request):
    if request.user.role != 'dept_rep':
        return redirect('/')
    rep  = get_object_or_404(DepartmentRep, user=request.user)
    dept = rep.department
    today = date.today()

    txns = dept.transactions.all()
    month_txns    = txns.filter(date__year=today.year, date__month=today.month)
    month_expense = float(month_txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
    month_income  = float(month_txns.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
    total_budget  = float(dept.total_budget())
    remaining     = max(total_budget - month_expense, 0)
    pct_used      = round((month_expense / total_budget * 100)) if total_budget > 0 else 0
    pct_used      = min(pct_used, 100)
    budget_exceeded = month_expense >= total_budget and total_budget > 0

    
    labels, inc_data, exp_data = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        inc_data.append(float(txns.filter(date=d, type='income').aggregate(Sum('amount'))['amount__sum'] or 0))
        exp_data.append(float(txns.filter(date=d, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0))

    budget_requests = dept.budget_requests.all()[:5]

    return render(request, 'department/rep_dashboard.html', {
        'dept': dept, 'rep': rep,
        'month_expense': month_expense, 'month_income': month_income,
        'total_budget': total_budget, 'remaining': remaining,
        'pct_used': pct_used, 'budget_exceeded': budget_exceeded,
        'recent_txns': txns[:8],
        'budget_requests': budget_requests,
        'today': today,
        'labels':   json.dumps(labels),
        'inc_data': json.dumps(inc_data),
        'exp_data': json.dumps(exp_data),
    })


@login_required
def add_dept_transaction(request):
    if request.user.role != 'dept_rep':
        return redirect('/')
    rep  = get_object_or_404(DepartmentRep, user=request.user)
    dept = rep.department
    today = date.today()

    
    month_expense = float(dept.transactions.filter(
        date__year=today.year, date__month=today.month, type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0)
    budget_exceeded = month_expense >= float(dept.total_budget()) and float(dept.total_budget()) > 0

    form = DeptTransactionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        txn_type = form.cleaned_data['type']
        amount   = float(form.cleaned_data['amount'])

        
        if txn_type == 'expense' and budget_exceeded:
            messages.error(request, 'Budget exceeded! You cannot add more expenses. Request more budget first.')
            return redirect('department:rep_dashboard')

        
        if txn_type == 'expense' and float(dept.total_budget()) > 0:
            if month_expense + amount > float(dept.total_budget()):
                messages.error(request, f'This expense (৳{amount}) will exceed your budget! Request more budget first.')
                return redirect('department:add_dept_transaction')

        txn = form.save(commit=False)
        txn.department = dept
        txn.added_by   = request.user
        txn.save()
        messages.success(request, 'Transaction added!')
        return redirect('department:rep_dashboard')

    return render(request, 'department/add_dept_transaction.html', {
        'form': form, 'dept': dept,
        'budget_exceeded': budget_exceeded,
        'month_expense': month_expense,
        'total_budget': float(dept.total_budget()),
    })


@login_required
def request_budget(request):
    if request.user.role != 'dept_rep':
        return redirect('/')
    rep  = get_object_or_404(DepartmentRep, user=request.user)
    dept = rep.department
    form = BudgetRequestForm(request.POST or None)
    if form.is_valid():
        br = form.save(commit=False)
        br.department   = dept
        br.requested_by = request.user
        br.save()
        messages.success(request, 'Budget request submitted!')
        return redirect('department:rep_dashboard')
    return render(request, 'department/request_budget.html', {'form': form, 'dept': dept})


@login_required
def delete_dept_transaction(request, pk):
    rep = get_object_or_404(DepartmentRep, user=request.user)
    txn = get_object_or_404(DepartmentTransaction, pk=pk, department=rep.department)
    txn.delete()
    messages.success(request, 'Transaction deleted.')
    return redirect('department:rep_dashboard')

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import date

@login_required
def monthly_report(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)

    year = int(request.GET.get('year', date.today().year))
    month = request.GET.get('month')

    txns = dept.transactions.filter(date__year=year)

    
    if month:
        txns = txns.filter(date__month=int(month))

    monthly_data = []

    
    if month:
        income = txns.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = txns.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

        monthly_data.append({
            'month': f"{year}-{month}",
            'income': float(income),
            'expense': float(expense),
            'net': float(income) - float(expense),
        })

    else:
        
        for m in range(1, 13):
            m_txn = txns.filter(date__month=m)

            income = m_txn.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
            expense = m_txn.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

            monthly_data.append({
                'month': f"{year}-{m}",
                'income': float(income),
                'expense': float(expense),
                'net': float(income) - float(expense),
            })

    return render(request, 'department/monthly_report.html', {
        'dept': dept,
        'monthly_data': monthly_data,
        'year': year,
        'month': int(month) if month else None,
    })
